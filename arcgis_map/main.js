require([
    "esri/WebScene",
    "esri/views/SceneView",
    "esri/geometry/Point",
    "esri/geometry/Extent",
    "esri/Graphic",
    "esri/layers/FeatureLayer",
    "esri/layers/CSVLayer",
    "esri/layers/VectorTileLayer",
    "esri/layers/GraphicsLayer",
    "esri/layers/support/LabelClass",
    "esri/symbols/WebStyleSymbol",
    "esri/widgets/Search",
    "esri/widgets/Expand",
    "esri/widgets/DirectLineMeasurement3D",
    "esri/widgets/ElevationProfile",
    "esri/widgets/LineOfSight",
    "esri/widgets/Legend",
    "esri/widgets/BasemapGallery",
    "esri/widgets/Sketch",
    "esri/widgets/Editor",
    "esri/widgets/LayerList",
    "esri/layers/BaseElevationLayer",
    "esri/layers/ElevationLayer",
    "esri/geometry/geometryEngine"
], function (WebScene, SceneView, Point, Extent, Graphic,
    FeatureLayer, CSVLayer, VectorTileLayer, GraphicsLayer, LabelClass,
    WebStyleSymbol,
    Search, Expand, DirectLineMeasurement3D, ElevationProfile, LineOfSight, Legend, BasemapGallery, Sketch, Editor, LayerList,
    BaseElevationLayer, ElevationLayer, geometryEngine) {

    const ExaggeratedElevationLayer = BaseElevationLayer.createSubclass({
        properties: {
            exaggeration: 5
        },

        load: function () {
            this._elevation = new ElevationLayer({
                url: "//elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/TopoBathy3D/ImageServer"
            });

            // wait for the elevation layer to load before resolving load()
            this.addResolvingPromise(
                this._elevation.load().then(() => {
                    // get tileInfo, spatialReference and fullExtent from the elevation service
                    // this is required for elevation services with a custom spatialReference
                    this.tileInfo = this._elevation.tileInfo;
                    this.spatialReference = this._elevation.spatialReference;
                    this.fullExtent = this._elevation.fullExtent;
                })
            );

            return this;
        },

        // This method must be implemented for every elevation service
        fetchTile: function (level, row, col, options) {
            // calls fetchTile() on the elevationlayer for the tiles
            // the data is returned as a heightmap
            return this._elevation.fetchTile(level, row, col, options)
                .then((data) => {
                    // multiply every value by the exaggeration
                    for (let i = 0; i < data.values.length; i++) {
                        data.values[i] = data.values[i] * this.exaggeration;
                    }

                    return data;
                });
        }
    });

    // Create the web scene with custom elevation layer
    var map = new WebScene({
        ground: {
            layers: [new ExaggeratedElevationLayer()]
        },
        basemap: "topo-3d"
    });
    
    // Create the view
    var view = new SceneView({
        container: "viewDiv",
        qualityProfile: "high",
        // qualityProfile: "low",
        map: map,
        camera: {
            position: {
                latitude: -23.999131658709025,
                longitude: -46.55439762885409,
                z: 24920.23517484404
            },
            tilt: 56.999999999999496
        },
        environment: {
            lighting: {
                date: new Date("June 15, 2015 12:00:00 EDT"),
                directShadowsEnabled: true,
                ambientOcclusionEnabled: true
            }
        }
    });

    // Function to get camera position
    function getCameraPosition() {
        return {
            camera: {
                position: {
                    latitude: view.camera.position.latitude,
                    longitude: view.camera.position.longitude,
                    z: view.camera.position.z
                },
                tilt: view.camera.tilt
            }
        }

    }

    // Pass view to global variable
    window.view = view;
    window.getCameraPosition = getCameraPosition;

    /**********************************************
   * WATERWAYS
   **********************************************/

    var mapLayers = []

    // layerWaterways
    const layerWaterways = new FeatureLayer({
        url: "https://services6.arcgis.com/Do88DoK2xjTUCXd1/arcgis/rest/services/OSM_SA_Waterways/FeatureServer",
        minScale: 10000,
        elevationInfo: {
            mode: "relative-to-scene"
        },
        outFields: ["*"],
        renderer: {
            type: "simple",
            symbol: {
                type: "simple-line",
                color: "#4AA0E8",
                width: 2
            }
        },
        labelingInfo: [{
            labelExpressionInfo: {
                value: ""
            },
            symbol: {
                type: "label-3d",
                // autocasts as new LabelSymbol3D()
                symbolLayers: [{
                    type: "text",
                    // autocasts as new TextSymbol3DLayer()
                    material: {
                        color: "white"
                    },
                    // we set a halo on the font to make the labels more visible with any kind of background
                    halo: {
                        size: 1,
                        color: [50, 50, 50]
                    },
                    size: 10
                }]
            }
        }],
        popupTemplate: {
            // autocasts as new PopupTemplate()
            title: "{name}",
            content: [{
                type: "fields",
                fieldInfos: [{
                    fieldName: "objectid",
                    label: "objectid"
                }, {
                    fieldName: "name",
                    label: "name"
                }, {
                    fieldName: "osm_id2",
                    label: "osm_id2"
                }, {
                    fieldName: "access",
                    label: "access"
                }, {
                    fieldName: "bicycle",
                    label: "bicycle"
                }, {
                    fieldName: "bridge",
                    label: "bridge"
                }, {
                    fieldName: "bus",
                    label: "bus"
                }, {
                    fieldName: "crossing",
                    label: "crossing"
                }, {
                    fieldName: "foot",
                    label: "foot"
                }, {
                    fieldName: "footway",
                    label: "footway"
                }, {
                    fieldName: "highway",
                    label: "highway"
                }, {
                    fieldName: "lanes",
                    label: "lanes"
                }, {
                    fieldName: "layer",
                    label: "layer"
                }, {
                    fieldName: "maxspeed",
                    label: "maxspeed"
                }, {
                    fieldName: "oneway",
                    label: "oneway"
                }, {
                    fieldName: "public_transport",
                    label: "public_transport"
                }, {
                    fieldName: "service",
                    label: "service"
                }, {
                    fieldName: "source",
                    label: "source"
                }, {
                    fieldName: "surface",
                    label: "surface"
                }, {
                    fieldName: "tracktype",
                    label: "tracktype"
                }, {
                    fieldName: "width",
                    label: "width"
                }]
            }]
        },
    });

    /**********************************************
     * Monitoring Stations Layer
     **********************************************/

    const stationsRenderer = {
        type: "simple",
        symbol: {
            type: "point-3d",
            symbolLayers: [{
                type: "icon",
                resource: { primitive: "circle" },
                material: { color: "#D13470" },
                size: 10,
                outline: {
                    color: "white",
                    size: 2
                }
            }],
            verticalOffset: {
                screenLength: 60
            },
            callout: {
                type: "line", // autocasts as new LineCallout3D()
                color: "white",
                size: 1,
                border: {
                    color: "#D13470"
                }
            }
        }
    };

    const stationsPopupTemplate = {
        title: "{name} - {elevation}m",
        content: [
            {
                type: "fields",
                fieldInfos: [
                    {
                        fieldName: "posto",
                        label: "Posto"
                    },
                    {
                        fieldName: "Código API - FLU",
                        label: "Código API"
                    },
                    {
                        fieldName: "minDate",
                        label: "Data Inicial"
                    }
                ]
            }
        ]
    };

    function transformStationData(stations) {
        return stations.map(station => ({
            geometry: {
                type: "point",
                latitude: station.latitude,
                longitude: station.longitude,
                spatialReference: { wkid: 4326 }
            },
            attributes: {
                name: station.name,
                elevation: station.elevation
            }
        }));
    }

    const stationsLayer = new FeatureLayer({
        title: "Estações de Monitoramento",
        source: transformStationData(window.stations_data),
        copyright: "OpenStreetMap",
        spatialReference: { wkid: 4326 },
        objectIdField: "ObjectID",
        fields: [{
            name: "ObjectID",
            type: "oid"
        }, {
            name: "name",
            type: "string"
        }, {
            name: "elevation",
            type: "double"
        }],
        popupTemplate: stationsPopupTemplate,
        elevationInfo: {
            mode: "relative-to-ground"
        },
        returnZ: false,
        screenSizePerspectiveEnabled: false,
        renderer: stationsRenderer,
        labelingInfo: [{
            labelExpressionInfo: {
                value: "{name} - {elevation}m"
            },
            symbol: {
                type: "label-3d",
                symbolLayers: [{
                    type: "text",
                    material: {
                        color: "white"
                    },
                    halo: {
                        size: 3,
                        color: "black"
                    },
                    size: 11
                }]
            }
        }]
    });

    // Station navigation state
    let currentStationIndex = -1;
    let stationFeatures = [];

    // Function to navigate to a station
    function navigateToStation(index) {
        if (stationFeatures.length === 0) return;

        currentStationIndex = index;
        const station = stationFeatures[currentStationIndex];

        // Highlight current station
        stationsLayer.renderer = {
            type: "simple",
            symbol: {
                type: "point-3d",
                symbolLayers: [{
                    type: "icon",
                    resource: { primitive: "circle" },
                    material: { color: station.attributes.ObjectId === stationFeatures[currentStationIndex].attributes.ObjectId ? "#4CE13F" : "#D13470" },
                    size: 10,
                    outline: {
                        color: "white",
                        size: 2
                    }
                }],
                verticalOffset: {
                    screenLength: 60
                },
                callout: {
                    type: "line",
                    color: "white",
                    size: 1,
                    border: {
                        color: "#D13470"
                    }
                }
            }
        };

        // Find intersecting waterway
        const query = layerWaterways.createQuery();
        query.geometry = station.geometry;
        query.distance = 80;
        query.units = "meters";
        query.spatialRelationship = "within";
        query.spatialRelationship = "intersects";
        query.returnGeometry = true;
        query.outFields = ["*"];

        layerWaterways.queryFeatures(query).then(function (result) {
            if (result.features.length > 0) {
                // Combine all intersecting waterways into a single geometry
                const combinedGeometry = result.features.reduce((union, feature, index) => {
                    return index === 0 ? feature.geometry : geometryEngine.union(union, feature.geometry);
                }, null);

                // Update elevation profile with combined waterway geometry
                widgetElevationProfile.input = {
                    geometry: combinedGeometry,
                    layer: layerWaterways
                };
            }
        });

        // Navigate camera to station
        view.goTo({
            target: station.geometry,
            zoom: 16,
            tilt: 40
        }, {
            duration: 1000,
            easing: "ease-out"
        });

    }

    // Previous station button
    const prevButton = document.createElement("calcite-button");
    prevButton.setAttribute("appearance", "solid");
    prevButton.setAttribute("color", "blue");
    prevButton.setAttribute("icon-start", "chevron-left");
    prevButton.innerHTML = "Previous";
    prevButton.onclick = () => {
        if (currentStationIndex > 0) {
            navigateToStation(currentStationIndex - 1);
        }
    };

    // Next station button
    const nextButton = document.createElement("calcite-button");
    nextButton.setAttribute("appearance", "solid");
    nextButton.setAttribute("color", "blue");
    nextButton.setAttribute("icon-end", "chevron-right");
    nextButton.innerHTML = "Next";
    nextButton.onclick = () => {
        if (currentStationIndex < stationFeatures.length - 1) {
            navigateToStation(currentStationIndex + 1);
        }
    };

    // Overview button
    const overviewButton = document.createElement("calcite-button");
    overviewButton.setAttribute("appearance", "solid");
    overviewButton.setAttribute("color", "blue");
    overviewButton.setAttribute("icon-start", "zoom-out-fixed");
    overviewButton.innerHTML = "Overview";
    overviewButton.onclick = () => {
        view.goTo({
            position: {
                latitude: -23.999131658709025,
                longitude: -46.55439762885409,
                z: 24920.23517484404
            },
            tilt: 56.999999999999496
        }, {
            duration: 1000,
            easing: "ease-out"
        });
    };

    // Add navigation container
    const navContainer = document.createElement("div");
    navContainer.style.display = "flex";
    navContainer.style.gap = "8px";
    navContainer.appendChild(prevButton);
    navContainer.appendChild(overviewButton);
    navContainer.appendChild(nextButton);

    view.ui.add(navContainer, "bottom-left");

    // Load stations when layer is ready
    // Create stations list container
    const stationsListContainer = document.createElement("div");
    stationsListContainer.style.backgroundColor = "#fff";
    stationsListContainer.style.padding = "12px";
    stationsListContainer.style.maxHeight = "300px";
    stationsListContainer.style.overflowY = "auto";
    stationsListContainer.style.width = "250px";

    // Create stations list
    const stationsList = document.createElement("calcite-list");
    stationsList.setAttribute("selection-mode", "single");
    stationsListContainer.appendChild(stationsList);

    // Transform stations data
    stationFeatures = transformStationData(window.stations_data);

    // Create list items for each station
    stationFeatures.forEach((station, index) => {
        const listItem = document.createElement("calcite-list-item");
        listItem.setAttribute("label", station.attributes.name);
        listItem.setAttribute("description", `Elevation: ${station.attributes.elevation}m`);
        listItem.setAttribute("value", index);
        listItem.onclick = () => navigateToStation(index);
        stationsList.appendChild(listItem);
    });

    // Create stations list expand widget
    const stationsListExpand = new Expand({
        view: view,
        content: stationsListContainer,
        expandIcon: "list",
        group: "top-right",
        expanded: false
    });

    view.ui.add(stationsListExpand, "bottom-right");

    // Layers in map
    mapLayers.push(layerWaterways);
    mapLayers.push(stationsLayer);

    /**********************************************
   * WIDGETS
   **********************************************/

    // ElevationProfile
    const widgetElevationProfile = new ElevationProfile({
        view: view
    });
    view.ui.add(new Expand({
        view: view,
        content: widgetElevationProfile,
        expanded: true,
        expandTooltip: "Análise de elevação",
        expandIconClass: "esri-icon-elevation-profile",
    }), "top-right");

    // Layer List
    const widgetLayerList = new LayerList({
        view: view
    });
    view.ui.add(new Expand({
        view: view,
        content: widgetLayerList,
        expandTooltip: "Camadas"
    }), "top-right");

    // Basemap
    const widgetBasemapGallery = new BasemapGallery({
        view: view
    });
    view.ui.add(new Expand({
        view: view,
        content: widgetBasemapGallery,
        expandTooltip: "Trocar basemap"
    }), "top-right");

    // Add layer
    map.addMany(mapLayers);
});
