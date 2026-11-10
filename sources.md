# Sources

## Primary source for every figure in this brief

1. **Sidewalks Inventory (Sidewalks_View), Metropolitan Government of Nashville and Davidson County, Nashville Open Data Portal.** ArcGIS FeatureServer layer 0, services2.arcgis.com/HdTo6HJqh92wn4D8. Snapshot pulled November 10, 2026: 14,938 records, verified at pull time against the server's own returnCountOnly count (14,938). Layer metadata archived in this package at data/source-metadata-layer.json; the layer's data was last edited November 9, 2026 per the service listing (editingInfo.dataLastEditDate).
   - Service: https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Sidewalks_View/FeatureServer/0
   - Fields used: OnStreet, FromStreet, ToStreet, Side, Condition, District, DateRepaired, RepairScoreWalkNBike, SidewalkWidth, RepairConstructionCost, Shape__Length. The Shape__Length field alias in the metadata is "Length (ft)" and the service spatial reference is EPSG:2274, which is the basis for reporting lengths in feet; all mile figures are derived (feet / 5,280) and labeled derived. The metadata does not define the Condition values or the population rules for the score and cost fields; the brief records that absence and assigns no definitions.
   - Personal-data check: the layer's fields are street names, segment condition and repair fields, district, and length. It carries no personal data (no individual names, contact fields, or parcel-owner fields), so the raw snapshot CSV ships in this repository.

## Comparison source (published Machine Readable brief only)

2. **Nashville Traffic Accidents (Machine Readable, November 2, 2026)** - 222,903 reported crashes, January 1, 2019 to October 31, 2026; 926 people killed, of whom 280 (30.2 percent) were pedestrians. Used at city level only; no district-level join was performed (the sidewalk District field is a Metro Council district; the crash layer's published geography is precinct and ZIP code). Repository: https://github.com/adowlen/nashville-traffic-accidents-data-brief

## Repository and license

Full code, charts, panels, and verification notes: https://github.com/adowlen/nashville-sidewalks-data-brief
Brief text and data products: CC BY 4.0 (LICENSE in the package). The underlying records are published by Metro Nashville as government open data.
