# Corporation and Municipality API Implementation

This document describes the implementation of Corporation and Municipality entities in the Heaven Connect API, extending the existing location hierarchy.

## Overview

The location hierarchy now includes:
- **Districts** (existing)
- **Grama Panchayats** (existing)
- **Corporations** (new)
- **Municipalities** (new)

All local bodies (Corporations and Municipalities) are connected to Districts, maintaining the hierarchical structure.

## Location Hierarchy & Relationships

### Complete Location Structure
```
State
└── District (1)
    ├── Grama Panchayats (Many)
    ├── Corporations (Many)
    └── Municipalities (Many)
```

### Relationship Flow Diagram
```
┌─────────────────┐
│      State      │
└─────────┬───────┘
          │
          │ 1:Many
          ▼
┌─────────────────┐
│    District     │ ◄─── Primary Entity
│  - id (PK)      │
│  - name         │
│  - state        │
│  - code         │
└─────────┬───────┘
          │
          │ 1:Many (3 separate relationships)
          ├─────────────────────────────────────┐
          │                                     │
          ▼                                     ▼
┌─────────────────┐                    ┌─────────────────┐
│ Grama Panchayats│                    │  Corporations   │
│ - id (PK)       │                    │ - id (PK)       │
│ - district_id   │                    │ - district_id   │
│ - name          │                    │ - name          │
│ - population    │                    │ - mayor_name    │
│ - area_sq_km    │                    │ - established_yr│
└─────────────────┘                    └─────────────────┘
          │
          │
          ▼
┌─────────────────┐
│  Municipalities │
│ - id (PK)       │
│ - district_id   │
│ - name          │
│ - chairman_name │
│ - municipality_ │
│   type          │
└─────────────────┘
```

### Database Relationships

#### Foreign Key Constraints
- **Grama Panchayats** → `district_id` references `districts.id`
- **Corporations** → `district_id` references `districts.id`  
- **Municipalities** → `district_id` references `districts.id`

#### SQLAlchemy Relationships
```python
# District Model
class District(Base):
    # One-to-Many relationships
    grama_panchayats: Mapped[List["GramaPanchayat"]] = relationship(
        "GramaPanchayat", 
        back_populates="district", 
        cascade="all, delete-orphan"
    )
    corporations: Mapped[List["Corporation"]] = relationship(
        "Corporation", 
        back_populates="district", 
        cascade="all, delete-orphan"
    )
    municipalities: Mapped[List["Municipality"]] = relationship(
        "Municipality", 
        back_populates="district", 
        cascade="all, delete-orphan"
    )

# Local Body Models
class GramaPanchayat(Base):
    district: Mapped["District"] = relationship("District", back_populates="grama_panchayats")

class Corporation(Base):
    district: Mapped["District"] = relationship("District", back_populates="corporations")

class Municipality(Base):
    district: Mapped["District"] = relationship("District", back_populates="municipalities")
```

### Data Flow Examples

#### 1. Creating a Complete Location Hierarchy
```python
# Step 1: Create District
district_data = {
    "name": "Ernakulam",
    "state": "Kerala",
    "code": "EKM",
    "description": "Ernakulam District"
}
district = await district_service.create(db, obj_in=district_data)

# Step 2: Create Grama Panchayats
panchayat_data = {
    "name": "Kochi Grama Panchayat",
    "district_id": district.id,
    "population": 50000,
    "area_sq_km": 15.5
}
panchayat = await grama_panchayat_service.create(db, obj_in=panchayat_data)

# Step 3: Create Corporation
corporation_data = {
    "name": "Kochi Corporation",
    "district_id": district.id,
    "mayor_name": "M. Anilkumar",
    "population": 677381
}
corporation = await corporation_service.create(db, obj_in=corporation_data)

# Step 4: Create Municipality
municipality_data = {
    "name": "Aluva Municipality",
    "district_id": district.id,
    "chairman_name": "T. J. Vinod",
    "municipality_type": "Grade A"
}
municipality = await municipality_service.create(db, obj_in=municipality_data)
```

#### 2. Retrieving Complete District Information
```python
# Get district with all local bodies
district_with_all = await district_service.get_with_relationships(
    db, 
    district_id=1,
    include=["grama_panchayats", "corporations", "municipalities"]
)

# Result structure:
{
    "id": 1,
    "name": "Ernakulam",
    "state": "Kerala",
    "grama_panchayats": [
        {"id": 1, "name": "Kochi Grama Panchayat", "population": 50000},
        {"id": 2, "name": "Fort Kochi Panchayat", "population": 25000}
    ],
    "corporations": [
        {"id": 1, "name": "Kochi Corporation", "mayor_name": "M. Anilkumar"}
    ],
    "municipalities": [
        {"id": 1, "name": "Aluva Municipality", "chairman_name": "T. J. Vinod"}
    ]
}
```

#### 3. Cross-Entity Queries
```python
# Get all local bodies for a district
district_id = 1

# Get all grama panchayats
panchayats = await grama_panchayat_service.get_by_district(db, district_id)

# Get all corporations  
corporations = await corporation_service.get_by_district(db, district_id)

# Get all municipalities
municipalities = await municipality_service.get_by_district(db, district_id)

# Get total population of district
total_population = sum([
    p.population or 0 for p in panchayats
] + [
    c.population or 0 for c in corporations  
] + [
    m.population or 0 for m in municipalities
])
```

### API Endpoint Relationships

#### District-Centric Endpoints
- `GET /api/v1/districts/{id}/with-panchayats` - District + Grama Panchayats
- `GET /api/v1/districts/{id}/with-all-local-bodies` - District + All Local Bodies
- `GET /api/v1/grama-panchayats/district/{district_id}` - Panchayats by District
- `GET /api/v1/corporations/district/{district_id}` - Corporations by District  
- `GET /api/v1/municipalities/district/{district_id}` - Municipalities by District

#### Cross-Entity Filtering
```http
# Get all local bodies with population > 100,000
GET /api/v1/grama-panchayats/?min_population=100000
GET /api/v1/corporations/?min_population=100000
GET /api/v1/municipalities/?min_population=100000

# Get all local bodies established in 1950
GET /api/v1/corporations/?established_year=1950
GET /api/v1/municipalities/?established_year=1950

# Search across all local bodies
GET /api/v1/grama-panchayats/?search=Kochi
GET /api/v1/corporations/?search=Kochi  
GET /api/v1/municipalities/?search=Kochi
```

### Data Integrity Rules

#### Cascade Operations
- **District Deletion**: When a district is deleted, all associated local bodies are also deleted (cascade="all, delete-orphan")
- **Soft Delete**: All entities support soft delete via `is_active` flag
- **Referential Integrity**: Foreign key constraints prevent orphaned records

#### Validation Rules
- **District ID**: Must exist before creating local bodies
- **Unique Codes**: Each local body type has unique code constraints
- **Population Consistency**: Population data should be consistent across related entities
- **Geographic Consistency**: Area calculations should align with district boundaries

### Performance Considerations

#### Indexing Strategy
```sql
-- Primary indexes
CREATE INDEX ix_districts_state ON districts(state);
CREATE INDEX ix_grama_panchayats_district_id ON grama_panchayats(district_id);
CREATE INDEX ix_corporations_district_id ON corporations(district_id);
CREATE INDEX ix_municipalities_district_id ON municipalities(district_id);

-- Search indexes
CREATE INDEX ix_grama_panchayats_name ON grama_panchayats(name);
CREATE INDEX ix_corporations_name ON corporations(name);
CREATE INDEX ix_municipalities_name ON municipalities(name);

-- Filter indexes
CREATE INDEX ix_grama_panchayats_population ON grama_panchayats(population);
CREATE INDEX ix_corporations_population ON corporations(population);
CREATE INDEX ix_municipalities_population ON municipalities(population);
```

#### Query Optimization
- Use `select_related()` for district information when fetching local bodies
- Implement pagination for large datasets
- Use database-level filtering instead of application-level filtering
- Consider caching for frequently accessed district hierarchies

## Database Schema

### Corporation Table
```sql
CREATE TABLE corporations (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    district_id INTEGER NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    population INTEGER,
    area_sq_km FLOAT,
    mayor_name VARCHAR(100),
    established_year INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (district_id) REFERENCES districts(id)
);
```

### Municipality Table
```sql
CREATE TABLE municipalities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    district_id INTEGER NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    population INTEGER,
    area_sq_km FLOAT,
    chairman_name VARCHAR(100),
    established_year INTEGER,
    municipality_type VARCHAR(50), -- Grade A, Grade B, Grade C
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (district_id) REFERENCES districts(id)
);
```

## API Endpoints

### Corporation Endpoints

#### Create Corporation
```http
POST /api/v1/corporations/
Content-Type: application/json

{
    "name": "Kochi Corporation",
    "district_id": 1,
    "code": "KOC001",
    "description": "Kochi Municipal Corporation",
    "population": 677381,
    "area_sq_km": 94.88,
    "mayor_name": "M. Anilkumar",
    "established_year": 1967,
    "is_active": true
}
```

#### Get All Corporations
```http
GET /api/v1/corporations/
GET /api/v1/corporations/?district_id=1
GET /api/v1/corporations/?search=Kochi
GET /api/v1/corporations/?min_population=100000&max_population=1000000
GET /api/v1/corporations/?established_year=1967
GET /api/v1/corporations/?mayor_name=Anilkumar
```

#### Get Corporation by ID
```http
GET /api/v1/corporations/{corporation_id}
```

#### Get Corporation with District
```http
GET /api/v1/corporations/{corporation_id}/with-district
```

#### Update Corporation
```http
PUT /api/v1/corporations/{corporation_id}
Content-Type: application/json

{
    "mayor_name": "New Mayor Name",
    "population": 700000
}
```

#### Delete Corporation (Soft Delete)
```http
DELETE /api/v1/corporations/{corporation_id}
```

#### Get Corporations by District
```http
GET /api/v1/corporations/district/{district_id}
```

### Municipality Endpoints

#### Create Municipality
```http
POST /api/v1/municipalities/
Content-Type: application/json

{
    "name": "Aluva Municipality",
    "district_id": 1,
    "code": "ALU001",
    "description": "Aluva Municipality",
    "population": 25000,
    "area_sq_km": 7.5,
    "chairman_name": "T. J. Vinod",
    "established_year": 1950,
    "municipality_type": "Grade A",
    "is_active": true
}
```

#### Get All Municipalities
```http
GET /api/v1/municipalities/
GET /api/v1/municipalities/?district_id=1
GET /api/v1/municipalities/?search=Aluva
GET /api/v1/municipalities/?min_population=10000&max_population=50000
GET /api/v1/municipalities/?established_year=1950
GET /api/v1/municipalities/?chairman_name=Vinod
GET /api/v1/municipalities/?municipality_type=Grade A
```

#### Get Municipality by ID
```http
GET /api/v1/municipalities/{municipality_id}
```

#### Get Municipality with District
```http
GET /api/v1/municipalities/{municipality_id}/with-district
```

#### Update Municipality
```http
PUT /api/v1/municipalities/{municipality_id}
Content-Type: application/json

{
    "chairman_name": "New Chairman Name",
    "municipality_type": "Grade B"
}
```

#### Delete Municipality (Soft Delete)
```http
DELETE /api/v1/municipalities/{municipality_id}
```

#### Get Municipalities by District
```http
GET /api/v1/municipalities/district/{district_id}
```

### Enhanced District Endpoints

#### Get District with All Local Bodies
```http
GET /api/v1/districts/{district_id}/with-all-local-bodies
```

This endpoint returns a district with all its associated:
- Grama Panchayats
- Corporations
- Municipalities

## Response Schemas

### Corporation Response
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "Kochi Corporation",
        "district_id": 1,
        "code": "KOC001",
        "description": "Kochi Municipal Corporation",
        "population": 677381,
        "area_sq_km": 94.88,
        "mayor_name": "M. Anilkumar",
        "established_year": 1967,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "message": "Corporation retrieved successfully"
}
```

### Municipality Response
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "Aluva Municipality",
        "district_id": 1,
        "code": "ALU001",
        "description": "Aluva Municipality",
        "population": 25000,
        "area_sq_km": 7.5,
        "chairman_name": "T. J. Vinod",
        "established_year": 1950,
        "municipality_type": "Grade A",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "message": "Municipality retrieved successfully"
}
```

## Features

### Search and Filtering
- **Search by name**: Find corporations/municipalities by partial name match
- **Filter by district**: Get all local bodies for a specific district
- **Population range**: Filter by minimum and maximum population
- **Established year**: Find local bodies established in a specific year
- **Leadership**: Search by mayor/chairman name
- **Municipality type**: Filter municipalities by grade/type
- **Active status**: Filter by active/inactive status

### Pagination
All list endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 100, max: 1000)

### Soft Delete
All delete operations are soft deletes - records are marked as inactive (`is_active = false`) rather than being physically removed from the database.

### Data Validation
- Name: 2-200 characters
- District ID: Must be a positive integer
- Code: Optional, max 20 characters, must be unique
- Population: Optional, must be positive
- Area: Optional, must be positive
- Established year: Optional, between 1800-2030
- Leadership names: Optional, max 100 characters

## Database Migration

To apply the database changes, run the migration:

```bash
# Using Alembic (recommended for production)
alembic upgrade head

# Or using the migration script directly
python app/migrations/create_corporation_municipality_tables.py
```

## Usage Examples

### Understanding the Relationship Flow

#### Complete Location Data Retrieval
```python
import requests

# 1. Get a district with all its local bodies
district_response = requests.get("http://localhost:8000/api/v1/districts/1/with-all-local-bodies")
district_data = district_response.json()

print("=== DISTRICT OVERVIEW ===")
print(f"District: {district_data['data']['name']}")
print(f"State: {district_data['data']['state']}")
print(f"Total Local Bodies: {len(district_data['data']['grama_panchayats']) + len(district_data['data']['corporations']) + len(district_data['data']['municipalities'])}")

print("\n=== GRAMA PANCHAYATS ===")
for panchayat in district_data['data']['grama_panchayats']:
    print(f"- {panchayat['name']} (Population: {panchayat.get('population', 'N/A')})")

print("\n=== CORPORATIONS ===")
for corporation in district_data['data']['corporations']:
    print(f"- {corporation['name']} (Mayor: {corporation.get('mayor_name', 'N/A')})")

print("\n=== MUNICIPALITIES ===")
for municipality in district_data['data']['municipalities']:
    print(f"- {municipality['name']} (Chairman: {municipality.get('chairman_name', 'N/A')})")
```

#### Cross-Entity Analysis
```python
# Analyze population distribution across all local bodies
def analyze_district_population(district_id):
    # Get all local bodies for the district
    panchayats = requests.get(f"http://localhost:8000/api/v1/grama-panchayats/district/{district_id}").json()
    corporations = requests.get(f"http://localhost:8000/api/v1/corporations/district/{district_id}").json()
    municipalities = requests.get(f"http://localhost:8000/api/v1/municipalities/district/{district_id}").json()
    
    # Calculate totals
    total_panchayat_pop = sum(p.get('population', 0) for p in panchayats['data'])
    total_corporation_pop = sum(c.get('population', 0) for c in corporations['data'])
    total_municipality_pop = sum(m.get('population', 0) for m in municipalities['data'])
    
    total_population = total_panchayat_pop + total_corporation_pop + total_municipality_pop
    
    print(f"=== POPULATION ANALYSIS FOR DISTRICT {district_id} ===")
    print(f"Grama Panchayats: {total_panchayat_pop:,} ({total_panchayat_pop/total_population*100:.1f}%)")
    print(f"Corporations: {total_corporation_pop:,} ({total_corporation_pop/total_population*100:.1f}%)")
    print(f"Municipalities: {total_municipality_pop:,} ({total_municipality_pop/total_population*100:.1f}%)")
    print(f"Total Population: {total_population:,}")

# Usage
analyze_district_population(1)
```

#### Hierarchical Data Creation
```python
# Create a complete location hierarchy
def create_location_hierarchy():
    # Step 1: Create District
    district_data = {
        "name": "Thiruvananthapuram",
        "state": "Kerala", 
        "code": "TVM",
        "description": "Capital District of Kerala"
    }
    district_response = requests.post("http://localhost:8000/api/v1/districts/", json=district_data)
    district = district_response.json()['data']
    print(f"Created District: {district['name']} (ID: {district['id']})")
    
    # Step 2: Create Grama Panchayats
    panchayats_data = [
        {"name": "Kazhakuttam Panchayat", "district_id": district['id'], "population": 45000},
        {"name": "Vizhinjam Panchayat", "district_id": district['id'], "population": 32000}
    ]
    
    for panchayat_data in panchayats_data:
        panchayat_response = requests.post("http://localhost:8000/api/v1/grama-panchayats/", json=panchayat_data)
        panchayat = panchayat_response.json()
        print(f"Created Panchayat: {panchayat['name']} (ID: {panchayat['id']})")
    
    # Step 3: Create Corporation
    corporation_data = {
        "name": "Thiruvananthapuram Corporation",
        "district_id": district['id'],
        "code": "TVM001",
        "mayor_name": "Arya Rajendran",
        "population": 743691,
        "established_year": 1940
    }
    corporation_response = requests.post("http://localhost:8000/api/v1/corporations/", json=corporation_data)
    corporation = corporation_response.json()['data']
    print(f"Created Corporation: {corporation['name']} (ID: {corporation['id']})")
    
    # Step 4: Create Municipalities
    municipalities_data = [
        {
            "name": "Neyyattinkara Municipality",
            "district_id": district['id'],
            "chairman_name": "R. Rajesh",
            "municipality_type": "Grade A",
            "population": 28000
        },
        {
            "name": "Attingal Municipality", 
            "district_id": district['id'],
            "chairman_name": "S. Suresh",
            "municipality_type": "Grade B",
            "population": 35000
        }
    ]
    
    for municipality_data in municipalities_data:
        municipality_response = requests.post("http://localhost:8000/api/v1/municipalities/", json=municipality_data)
        municipality = municipality_response.json()['data']
        print(f"Created Municipality: {municipality['name']} (ID: {municipality['id']})")
    
    return district['id']

# Usage
district_id = create_location_hierarchy()
```

### Creating a Corporation
```python
import requests

corporation_data = {
    "name": "Thiruvananthapuram Corporation",
    "district_id": 1,
    "code": "TVM001",
    "description": "Thiruvananthapuram Municipal Corporation",
    "population": 743691,
    "area_sq_km": 214.86,
    "mayor_name": "Arya Rajendran",
    "established_year": 1940,
    "is_active": True
}

response = requests.post(
    "http://localhost:8000/api/v1/corporations/",
    json=corporation_data
)
```

### Getting All Local Bodies for a District
```python
# Get district with all local bodies
response = requests.get(
    "http://localhost:8000/api/v1/districts/1/with-all-local-bodies"
)
district_data = response.json()

print(f"District: {district_data['data']['name']}")
print(f"Grama Panchayats: {len(district_data['data']['grama_panchayats'])}")
print(f"Corporations: {len(district_data['data']['corporations'])}")
print(f"Municipalities: {len(district_data['data']['municipalities'])}")
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (for deletes)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
    "detail": "Corporation with this code already exists"
}
```

## Testing

The API can be tested using:
1. **Swagger UI**: Visit `/docs` for interactive API documentation
2. **ReDoc**: Visit `/redoc` for detailed API documentation
3. **Postman/Insomnia**: Import the OpenAPI schema
4. **Python requests**: As shown in the examples above

## Future Enhancements

Potential future improvements:
1. **Ward-level data**: Add ward information for corporations
2. **Election data**: Track election cycles and results
3. **Financial data**: Add budget and revenue information
4. **Geographic data**: Add latitude/longitude coordinates
5. **Contact information**: Add phone numbers, email addresses
6. **Social media**: Add social media handles
7. **Performance metrics**: Add various KPIs and metrics
