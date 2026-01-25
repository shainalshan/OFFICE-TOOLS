import React, { useEffect, useState, useRef } from 'react';

const ThreeDViewer = () => {
    const cesiumContainer = useRef(null);
    const viewerRef = useRef(null);
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showUpload, setShowUpload] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [csrfToken, setCsrfToken] = useState('');

    useEffect(() => {
        // Get CSRF token
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };
        setCsrfToken(getCookie('csrftoken'));

        // Load Cesium
        const loadCesium = async () => {
            if (!window.Cesium) {
                // Load CSS
                const link = document.createElement('link');
                link.href = 'https://cesium.com/downloads/cesiumjs/releases/1.104/Build/Cesium/Widgets/widgets.css';
                link.rel = 'stylesheet';
                document.head.appendChild(link);

                // Load JS
                const script = document.createElement('script');
                script.src = 'https://cesium.com/downloads/cesiumjs/releases/1.104/Build/Cesium/Cesium.js';
                script.async = true;
                script.onload = initCesium;
                document.body.appendChild(script);
            } else {
                initCesium();
            }
        };

        loadCesium();

        return () => {
            if (viewerRef.current) {
                viewerRef.current.destroy();
                viewerRef.current = null;
            }
        };
    }, []);

    const initCesium = () => {
        if (!cesiumContainer.current || viewerRef.current) return;

        const Cesium = window.Cesium;

        // Token
        const token = window.django?.cesium_token;
        if (token) {
            Cesium.Ion.defaultAccessToken = token;
        }

        const viewer = new Cesium.Viewer(cesiumContainer.current, {
            terrainProvider: Cesium.createWorldTerrain(),
            infoBox: false,
            selectionIndicator: false,
            timeline: false,
            animation: false,
            baseLayerPicker: false,
            fullscreenButton: false,
            geocoder: false,
            homeButton: false,
            sceneModePicker: false,
            navigationHelpButton: false
        });

        viewerRef.current = viewer;

        // Default view (Dubai)
        viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(55.2708, 25.2048, 2000),
            orientation: {
                heading: Cesium.Math.toRadians(0.0),
                pitch: Cesium.Math.toRadians(-45.0),
            }
        });

        fetchProjects(viewer);
    };

    const fetchProjects = async (viewer) => {
        try {
            const response = await fetch('/3d/api/projects/');
            const data = await response.json();
            setProjects(data.projects || []);
            setLoading(false);
            renderProjects(viewer, data.projects || []);
        } catch (error) {
            console.error('Error fetching projects:', error);
            setLoading(false);
        }
    };

    const renderProjects = (viewer, projectList) => {
        const Cesium = window.Cesium;
        viewer.entities.removeAll();

        projectList.forEach(proj => {
            const position = Cesium.Cartesian3.fromDegrees(proj.lon, proj.lat, proj.alt);
            const isObj = proj.url.toLowerCase().endsWith('.obj');

            if (isObj) {
                viewer.entities.add({
                    name: proj.name,
                    position: position,
                    billboard: {
                        image: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
                        width: 32,
                        height: 32,
                        verticalOrigin: Cesium.VerticalOrigin.BOTTOM
                    },
                    description: `OBJ File: ${proj.name}`
                });
            } else {
                const heading = Cesium.Math.toRadians(proj.heading || 0);
                const pitch = 0;
                const roll = 0;
                const hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
                const orientation = Cesium.Transforms.headingPitchRollQuaternion(position, hpr);

                viewer.entities.add({
                    name: proj.name,
                    position: position,
                    orientation: orientation,
                    model: {
                        uri: proj.url,
                        scale: proj.scale || 1.0,
                        minimumPixelSize: 128,
                        maximumScale: 20000
                    }
                });
            }
        });
    };

    const flyToProject = (proj) => {
        if (!viewerRef.current) return;
        const Cesium = window.Cesium;

        viewerRef.current.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(proj.lon, proj.lat, (proj.alt || 0) + 500),
            orientation: { pitch: Cesium.Math.toRadians(-45.0) }
        });
    };

    return (
        <div className="relative h-[calc(100vh-120px)] w-full rounded-2xl overflow-hidden border border-slate-700 bg-slate-900">
            {/* Cesium Container */}
            <div ref={cesiumContainer} className="w-full h-full" />

            {/* Sidebar Overlay */}
            <div className="absolute top-4 left-4 w-80 bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-xl p-4 shadow-2xl flex flex-col max-h-[calc(100%-32px)]">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-white">3D Projects</h2>
                    <button
                        onClick={() => setShowUpload(!showUpload)}
                        className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-semibold"
                    >
                        {showUpload ? 'Close' : '+ Upload'}
                    </button>
                </div>

                {showUpload ? (
                    <div className="animate-fade-in space-y-4 overflow-y-auto pr-1">
                        <form action="/3d/" method="POST" encType="multipart/form-data" className="space-y-3">
                            <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

                            <div>
                                <label className="text-xs text-slate-400 font-medium">Project Name</label>
                                <input name="name" required className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" placeholder="My Project" />
                            </div>

                            <div>
                                <label className="text-xs text-slate-400 font-medium">Model File (.glb, .gltf, .obj)</label>
                                <input type="file" name="model_file" accept=".glb,.gltf,.obj" required className="w-full text-slate-400 text-xs file:mr-2 file:py-1 file:px-3 file:rounded-lg file:bg-slate-800 file:text-white file:border-0" />
                            </div>

                            <div className="grid grid-cols-2 gap-2">
                                <div>
                                    <label className="text-xs text-slate-400 font-medium">Latitude</label>
                                    <input type="number" step="any" name="latitude" defaultValue="25.2048" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-400 font-medium">Longitude</label>
                                    <input type="number" step="any" name="longitude" defaultValue="55.2708" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
                                </div>
                            </div>

                            <button type="submit" className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-2 rounded-lg font-medium text-sm hover:opacity-90">
                                Create Project
                            </button>
                        </form>
                    </div>
                ) : (
                    <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1">
                        {loading ? (
                            <p className="text-slate-500 text-sm">Loading projects...</p>
                        ) : projects.length === 0 ? (
                            <p className="text-slate-500 text-sm">No projects found.</p>
                        ) : (
                            projects.map(proj => (
                                <div
                                    key={proj.id}
                                    onClick={() => flyToProject(proj)}
                                    className="p-3 bg-slate-900/50 hover:bg-slate-800 border border-slate-800/50 rounded-lg cursor-pointer transition-all group"
                                >
                                    <h3 className="font-semibold text-slate-200 group-hover:text-indigo-400">{proj.name}</h3>
                                    <div className="flex justify-between items-center text-xs text-slate-500 mt-1">
                                        <span>{proj.lat.toFixed(4)}, {proj.lon.toFixed(4)}</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ThreeDViewer;
