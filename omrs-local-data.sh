#!/bin/bash

# This should be run from the webapp directory
mv ~/.OpenMRS ./data
mv ./data/openmrs-runtime.properties .
echo "application_data_directory=data" >> openmrs-runtime.properties