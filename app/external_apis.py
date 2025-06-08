"""
External API integrations for real-time disaster data
"""
import requests
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from app.models import ReliefRequest, DisasterType, Region, DisasterSeverity, RequestStatus
from app import db

logger = logging.getLogger(__name__)


class USGSEarthquakeAPI:
    """USGS Earthquake API integration"""
    
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    @classmethod
    def fetch_recent_earthquakes(cls, hours: int = 24, min_magnitude: float = 4.0) -> List[Dict]:
        """Fetch recent earthquakes from USGS API"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        params = {
            'format': 'geojson',
            'starttime': start_time.isoformat(),
            'endtime': end_time.isoformat(),
            'minmagnitude': min_magnitude,
            'orderby': 'time-asc'
        }
        
        try:
            response = requests.get(cls.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            earthquakes = []
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [])
                
                if len(coords) >= 2:
                    earthquakes.append({
                        'id': feature.get('id'),
                        'title': props.get('title', 'Earthquake'),
                        'magnitude': props.get('mag'),
                        'location': props.get('place', 'Unknown location'),
                        'latitude': coords[1],
                        'longitude': coords[0],
                        'depth': coords[2] if len(coords) > 2 else None,
                        'time': datetime.fromtimestamp(props.get('time', 0) / 1000, tz=timezone.utc),
                        'url': props.get('url'),
                        'significance': props.get('sig', 0)
                    })
            
            logger.info(f"Fetched {len(earthquakes)} earthquakes from USGS API")
            return earthquakes
            
        except Exception as e:
            logger.error(f"Error fetching USGS earthquake data: {e}")
            return []


class NOAAWeatherAPI:
    """NOAA Weather Alerts API integration"""
    
    BASE_URL = "https://api.weather.gov"
    HEADERS = {'User-Agent': 'CDRP-API/1.0 (disaster-relief@example.com)'}
    
    @classmethod
    def fetch_active_alerts(cls, area: Optional[str] = None) -> List[Dict]:
        """Fetch active weather alerts from NOAA API"""
        url = f"{cls.BASE_URL}/alerts/active"
        params = {}
        if area:
            params['area'] = area
            
        try:
            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            alerts = []
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geometry = feature.get('geometry')
                
                # Extract coordinates if available
                coordinates = None
                if geometry and geometry.get('type') == 'Polygon':
                    coords = geometry.get('coordinates', [[]])
                    if coords and len(coords[0]) > 0:
                        # Get center point of polygon
                        lats = [point[1] for point in coords[0]]
                        lons = [point[0] for point in coords[0]]
                        coordinates = f"{sum(lats)/len(lats)},{sum(lons)/len(lons)}"
                
                alerts.append({
                    'id': props.get('id'),
                    'title': props.get('headline', 'Weather Alert'),
                    'description': props.get('description', ''),
                    'event': props.get('event', 'Unknown'),
                    'severity': props.get('severity', 'Unknown'),
                    'urgency': props.get('urgency', 'Unknown'),
                    'areas': props.get('areaDesc', ''),
                    'coordinates': coordinates,
                    'onset': props.get('onset'),
                    'expires': props.get('expires'),
                    'instruction': props.get('instruction', ''),
                    'web_url': props.get('web')
                })
            
            logger.info(f"Fetched {len(alerts)} weather alerts from NOAA API")
            return alerts
            
        except Exception as e:
            logger.error(f"Error fetching NOAA weather alerts: {e}")
            return []


class DisasterDataIntegrator:
    """Integrates external disaster data into CDRP system"""
    
    @classmethod
    def import_earthquake_data(cls, min_magnitude: float = 4.0) -> int:
        """Import earthquake data and create relief requests"""
        earthquakes = USGSEarthquakeAPI.fetch_recent_earthquakes(
            hours=24, 
            min_magnitude=min_magnitude
        )
        
        if not earthquakes:
            return 0
        
        # Get earthquake disaster type
        earthquake_type = DisasterType.query.filter_by(code='EQ').first()
        if not earthquake_type:
            logger.error("Earthquake disaster type not found in database")
            return 0
        
        imported_count = 0
        
        for quake in earthquakes:
            # Check if already imported
            existing = ReliefRequest.query.filter(
                ReliefRequest.title.contains(f"Magnitude {quake['magnitude']}")
            ).filter(
                ReliefRequest.location.contains(quake['location'])
            ).first()
            
            if existing:
                continue
            
            # Determine severity based on magnitude
            severity = cls._earthquake_magnitude_to_severity(quake['magnitude'])
            
            # Find appropriate region (simplified - assign to Central for now)
            region = Region.query.filter_by(code='CR').first()
            if not region:
                continue
            
            # Get system user for automated imports
            system_user = cls._get_system_user()
            if not system_user:
                continue
            
            # Create relief request
            request = ReliefRequest(
                title=f"Earthquake Alert - Magnitude {quake['magnitude']}",
                description=f"Earthquake detected: {quake['title']}\n\n"
                           f"Magnitude: {quake['magnitude']}\n"
                           f"Depth: {quake['depth']} km\n"
                           f"Time: {quake['time']}\n"
                           f"Significance: {quake['significance']}\n\n"
                           f"More info: {quake['url']}",
                location=quake['location'],
                coordinates=f"{quake['latitude']},{quake['longitude']}",
                severity=severity,
                status=RequestStatus.PENDING,
                disaster_type_id=earthquake_type.id,
                region_id=region.id,
                created_by=system_user.id,
                predicted_by_ml=True,
                ml_confidence=0.95,
                priority_score=cls._calculate_earthquake_priority(quake),
                affected_population=cls._estimate_affected_population(quake),
                required_resources="Emergency response team, medical supplies, search and rescue equipment"
            )
            
            db.session.add(request)
            imported_count += 1
        
        try:
            db.session.commit()
            logger.info(f"Successfully imported {imported_count} earthquake alerts")
            return imported_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving earthquake data: {e}")
            return 0
    
    @classmethod
    def import_weather_alerts(cls, area: Optional[str] = None) -> int:
        """Import weather alerts and create relief requests"""
        alerts = NOAAWeatherAPI.fetch_active_alerts(area)
        
        if not alerts:
            return 0
        
        imported_count = 0
        
        for alert in alerts:
            # Skip non-emergency events
            if alert['severity'].lower() not in ['severe', 'extreme', 'moderate']:
                continue
            
            # Get appropriate disaster type
            disaster_type = cls._map_weather_event_to_disaster_type(alert['event'])
            if not disaster_type:
                continue
            
            # Check if already imported
            existing = ReliefRequest.query.filter(
                ReliefRequest.title.contains(alert['event'])
            ).filter(
                ReliefRequest.description.contains(alert['id'])
            ).first()
            
            if existing:
                continue
            
            # Find appropriate region
            region = Region.query.filter_by(code='CR').first()
            if not region:
                continue
            
            # Get system user
            system_user = cls._get_system_user()
            if not system_user:
                continue
            
            # Determine severity
            severity = cls._weather_severity_to_disaster_severity(alert['severity'])
            
            # Create relief request
            request = ReliefRequest(
                title=f"{alert['event']} - {alert['areas'][:100]}",
                description=f"Weather Alert ID: {alert['id']}\n\n"
                           f"{alert['description']}\n\n"
                           f"Severity: {alert['severity']}\n"
                           f"Urgency: {alert['urgency']}\n"
                           f"Areas: {alert['areas']}\n\n"
                           f"Instructions: {alert['instruction']}\n\n"
                           f"More info: {alert['web_url']}",
                location=alert['areas'][:255],
                coordinates=alert['coordinates'],
                severity=severity,
                status=RequestStatus.PENDING,
                disaster_type_id=disaster_type.id,
                region_id=region.id,
                created_by=system_user.id,
                predicted_by_ml=True,
                ml_confidence=0.90,
                priority_score=cls._calculate_weather_priority(alert),
                required_resources="Weather monitoring, evacuation support, emergency shelters"
            )
            
            db.session.add(request)
            imported_count += 1
        
        try:
            db.session.commit()
            logger.info(f"Successfully imported {imported_count} weather alerts")
            return imported_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving weather alert data: {e}")
            return 0
    
    @staticmethod
    def _earthquake_magnitude_to_severity(magnitude: float) -> DisasterSeverity:
        """Convert earthquake magnitude to disaster severity"""
        if magnitude >= 7.0:
            return DisasterSeverity.CRITICAL
        elif magnitude >= 6.0:
            return DisasterSeverity.HIGH
        elif magnitude >= 5.0:
            return DisasterSeverity.MEDIUM
        else:
            return DisasterSeverity.LOW
    
    @staticmethod
    def _weather_severity_to_disaster_severity(severity: str) -> DisasterSeverity:
        """Convert weather alert severity to disaster severity"""
        severity_lower = severity.lower()
        if severity_lower == 'extreme':
            return DisasterSeverity.CRITICAL
        elif severity_lower == 'severe':
            return DisasterSeverity.HIGH
        elif severity_lower == 'moderate':
            return DisasterSeverity.MEDIUM
        else:
            return DisasterSeverity.LOW
    
    @staticmethod
    def _calculate_earthquake_priority(quake: Dict) -> float:
        """Calculate priority score for earthquake based on magnitude and significance"""
        magnitude = quake.get('magnitude', 0)
        significance = quake.get('significance', 0)
        
        # Base score from magnitude (0-10 scale)
        mag_score = min(magnitude * 10, 100)
        
        # Significance factor (0-1000+ scale, normalize to 0-50)
        sig_score = min(significance / 20, 50)
        
        return mag_score + sig_score
    
    @staticmethod
    def _calculate_weather_priority(alert: Dict) -> float:
        """Calculate priority score for weather alert"""
        severity_scores = {
            'extreme': 100,
            'severe': 80,
            'moderate': 60,
            'minor': 40,
            'unknown': 30
        }
        
        urgency_scores = {
            'immediate': 50,
            'expected': 30,
            'future': 20,
            'past': 10,
            'unknown': 20
        }
        
        severity_score = severity_scores.get(alert.get('severity', '').lower(), 30)
        urgency_score = urgency_scores.get(alert.get('urgency', '').lower(), 20)
        
        return severity_score + urgency_score
    
    @staticmethod
    def _estimate_affected_population(quake: Dict) -> int:
        """Estimate affected population based on earthquake magnitude"""
        magnitude = quake.get('magnitude', 0)
        
        # Rough estimation based on historical data
        if magnitude >= 7.0:
            return 100000
        elif magnitude >= 6.0:
            return 50000
        elif magnitude >= 5.0:
            return 10000
        else:
            return 1000
    
    @staticmethod
    def _map_weather_event_to_disaster_type(event: str) -> Optional[DisasterType]:
        """Map weather event type to disaster type in database"""
        event_lower = event.lower()
        
        # Mapping of weather events to disaster type codes
        event_mappings = {
            'flood': 'FL',
            'flash flood': 'FL',
            'hurricane': 'HU',
            'tornado': 'TO',
            'blizzard': 'BZ',
            'wildfire': 'WF',
            'fire weather': 'WF',
            'drought': 'DR'
        }
        
        for keyword, code in event_mappings.items():
            if keyword in event_lower:
                return DisasterType.query.filter_by(code=code).first()
        
        # Default to flood for other water-related events
        if any(word in event_lower for word in ['rain', 'storm', 'water']):
            return DisasterType.query.filter_by(code='FL').first()
        
        return None
    
    @staticmethod
    def _get_system_user():
        """Get or create system user for automated imports"""
        from app.models import User, UserRole
        
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            # Create system user if it doesn't exist
            central_region = Region.query.filter_by(code='CR').first()
            system_user = User(
                username='system',
                email='system@cdrp.org',
                first_name='System',
                last_name='Automated',
                role=UserRole.ADMIN,
                region_id=central_region.id if central_region else None
            )
            system_user.set_password('system_auto_import')
            db.session.add(system_user)
            db.session.commit()
        
        return system_user