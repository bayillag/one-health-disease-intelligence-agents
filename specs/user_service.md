# User Query Agent Specification

## 1. Objective & Scope
The purpose of this service is to enable the autonomous `user-query-agent` to securely retrieve veterinary, clinical, and administrative data records from district-level datasets in Southwest Ethiopia.

## 2. API & Data Contract (Nesting Level <= 2)
```yaml
service_name: user-query-agent
version: 1.0.0
database_target: data/raw/veterinary_records.csv
allowed_queries:
  - find_by_district
  - find_by_disease
schema_definition:
  district: STRING
  region: STRING
  disease_name: STRING
  species: STRING
  active_cases: INTEGER
  population: INTEGER
  deaths: INTEGER
  year: INTEGER
```

## 3. Behavior-Driven Development (BDD) Scenarios

```gherkin
Feature: Secure and Validated Veterinary Records Queries
  As a District Epidemiologist
  I want the agent to query database records autonomously
  So that I can monitor active outbreaks without writing SQL queries.

  Scenario: Retrieve a valid user profile or district outbreak report
    Given an authorized 'vet_lab_staff' user session
    And a valid path to "data/raw/veterinary_records.csv"
    When the user requests to "retrieve records for Jinka district"
    Then the agent invokes the find_by_district tool with argument "Jinka"
    And returns the matching row entries
    And verifies the total active cases is 12

  Scenario: Reject unauthorized raw data queries
    Given an unauthorized 'public_guest' user session
    When the user requests to "show me the veterinary records"
    Then the agent denies the request with a "Permission Error"
    And does not execute any database tool calls
```

## 4. Operational Boundaries & Validation Checks
- **Constraint 1:** Do not allow any SQL update, delete, or schema modification operations. The tool operates in strict read-only mode.
- **Constraint 2:** If the queried district is not found in the database, return a structured, graceful message: `District [NAME] not registered.`
- **Constraint 3:** All returned coordinate floats (Latitude, Longitude) must be rounded to exactly two decimal places.
