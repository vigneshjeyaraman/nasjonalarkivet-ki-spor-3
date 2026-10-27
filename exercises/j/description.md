# Digitization Candidates Query

This query identifies units that are high-priority candidates for digitization based on user demand.

## What it returns
A list of units including:
- **Creator Name**: The entity that created the records.
- **Reference**: The combined series code and unit reference.
- **Date Range**: The years the unit covers.
- **Request Count**: Number of active requests for this unit since 2024-01-01.
- **County**: The associated county (defaults to '?' if unknown).

## Logic
1. **Demand Calculation**: It counts "open" requests (excluding rejected, cancelled, or done) per unit since the start of 2024.
2. **Prioritization**: A unit is selected if:
   - It is not yet digitized.
   - It is not restricted.
   - It is either older than 1960 OR belongs to a series with code 'A'.
   - The number of requests for this unit is above the average request count per unit (with a small buffer of -1).
3. **Ordering**: Sorted by highest demand first.
