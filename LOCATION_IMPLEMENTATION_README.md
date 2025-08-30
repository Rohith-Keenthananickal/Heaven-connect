# Location Implementation - Districts and Grama Panchayats

This document explains the implementation of the new location management system for districts and grama panchayats in the Heaven Connect platform.

## Overview

The location system consists of two main entities:
1. **Districts** - Administrative divisions within states
2. **Grama Panchayats** - Local self-government units within districts

## Features

- ✅ Complete CRUD operations for both entities
- ✅ Hierarchical relationship (District → Grama Panchayats)
- ✅ Search and filtering capabilities
- ✅ Soft delete functionality
- ✅ Input validation and error handling
- ✅ RESTful API design
- ✅ Comprehensive documentation
- ✅ Sample data and testing tools

## File Structure

```
app/
├── models/
│   ├── __init__.py (updated)
│   └── location.py (new) - District and GramaPanchayat models
├── schemas/
│   ├── __init__.py (updated)
│   ├── districts.py (new) - District Pydantic schemas
│   └── grama_panchayats.py (new) - GramaPanchayat Pydantic schemas
├── services/
│   ├── __init__.py (updated)
│   ├── districts_service.py (new) - District business logic
│   └── grama_panchayats_service.py (new) - GramaPanchayat business logic
├── routers/
│   ├── __init__.py (updated)
│   ├── districts.py (new) - District API endpoints
│   └── grama_panchayats.py (new) - GramaPanchayat API endpoints
└── migrations/
    └── create_location_tables.py (new) - Database migration script

main.py (updated) - Router registration
LOCATION_API.md (new) - Complete API documentation
test_location_api.py (new) - API testing script
```

## Database Schema

### Districts Table
```sql
CREATE TABLE districts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    state VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Grama Panchayats Table
```sql
CREATE TABLE grama_panchayats (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    district_id INTEGER NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    population INTEGER,
    area_sq_km FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
);
```

## Setup Instructions

### 1. Database Migration

Run the migration script to create the new tables:

```bash
cd app/migrations
python create_location_tables.py
```

This will:
- Create the `districts` and `grama_panchayats` tables
- Insert sample data for testing
- Set up proper indexes and foreign key constraints

### 2. Start the Application

```bash
python main.py
```

The new routers are automatically registered and available at:
- `/api/v1/districts/` - Districts API
- `/api/v1/grama-panchayats/` - Grama Panchayats API

### 3. Test the Implementation

Run the test script to verify everything works:

```bash
python test_location_api.py
```

## API Endpoints

### Districts
- `POST /districts/` - Create district
- `GET /districts/` - List all districts (with filtering)
- `GET /districts/{id}` - Get district by ID
- `GET /districts/{id}/with-panchayats` - Get district with panchayats
- `PUT /districts/{id}` - Update district
- `DELETE /districts/{id}` - Soft delete district

### Grama Panchayats
- `POST /grama-panchayats/` - Create panchayat
- `GET /grama-panchayats/` - List all panchayats (with filtering)
- `GET /grama-panchayats/{id}` - Get panchayat by ID
- `GET /grama-panchayats/{id}/with-district` - Get panchayat with district
- `PUT /grama-panchayats/{id}` - Update panchayat
- `DELETE /grama-panchayats/{id}` - Soft delete panchayat
- `GET /grama-panchayats/district/{district_id}` - Get panchayats by district

## Usage Examples

### Create a District
```bash
curl -X POST "http://localhost:8000/api/v1/districts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thiruvananthapuram",
    "state": "Kerala",
    "code": "TVM",
    "description": "Capital district of Kerala"
  }'
```

### Create a Grama Panchayat
```bash
curl -X POST "http://localhost:8000/api/v1/grama-panchayats/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kovalam",
    "district_id": 1,
    "code": "KVL",
    "description": "Famous beach destination",
    "population": 15000,
    "area_sq_km": 25.5
  }'
```

### Get Districts by State
```bash
curl "http://localhost:8000/api/v1/districts/?state=Kerala"
```

### Get Panchayats by District
```bash
curl "http://localhost:8000/api/v1/grama-panchayats/district/1"
```

## Key Features

### 1. Hierarchical Structure
- Districts contain multiple grama panchayats
- Cascade delete ensures data integrity
- Easy navigation between related entities

### 2. Flexible Filtering
- Filter by state, district, population range
- Search by name or description
- Pagination support for large datasets

### 3. Data Validation
- Input validation using Pydantic schemas
- Unique constraints on codes and names
- Proper error handling and messages

### 4. Soft Delete
- Records are marked as inactive rather than deleted
- Maintains data history and referential integrity
- Easy to restore if needed

### 5. Performance Optimization
- Database indexes on frequently queried fields
- Efficient relationship queries
- Pagination to handle large datasets

## Integration with Existing System

The new location system integrates seamlessly with the existing Heaven Connect platform:

- **User Profiles**: Area coordinators can specify their district and panchayat
- **Property Management**: Properties can be associated with specific locations
- **Search and Filtering**: Enhanced location-based property search
- **Reporting**: Location-based analytics and reporting

## Future Enhancements

Potential improvements for the location system:

1. **Geographic Data**: Add latitude/longitude coordinates
2. **Boundary Maps**: Store geographic boundaries for districts/panchayats
3. **Population Updates**: Regular population data updates
4. **Multi-language Support**: Local language names for locations
5. **Location Hierarchy**: Support for additional administrative levels
6. **Caching**: Redis caching for frequently accessed location data

## Troubleshooting

### Common Issues

1. **Migration Fails**: Ensure MySQL is running and credentials are correct
2. **API Not Found**: Check that routers are properly registered in main.py
3. **Database Errors**: Verify table structure and foreign key constraints
4. **Validation Errors**: Check request body format and required fields

### Debug Mode

Enable debug mode in your environment to see detailed error messages:

```bash
export DEBUG=true
python main.py
```

## Support

For issues or questions about the location implementation:

1. Check the API documentation in `LOCATION_API.md`
2. Run the test script to verify functionality
3. Check server logs for error details
4. Verify database connectivity and table structure

## Contributing

When extending the location system:

1. Follow the existing code patterns
2. Add appropriate tests for new functionality
3. Update documentation and schemas
4. Ensure backward compatibility
5. Follow the project's coding standards

---

**Note**: This implementation follows the existing project architecture and coding standards. All endpoints are RESTful and include proper error handling, validation, and documentation.
