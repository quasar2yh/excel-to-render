import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { DxfViewer } from 'dxf-viewer';
import './index.css';

const App = () => {
    const containerRef = useRef(null);
    const viewerRef = useRef(null);
    const [currentFile, setCurrentFile] = useState('/floor_plan.dxf');
    const [layers, setLayers] = useState([]);
    const [coords, setCoords] = useState({ x: 0, y: 0 });
    const [isLoading, setIsLoading] = useState(true);
    const [theme, setTheme] = useState('dark'); // 'dark' or 'store'
    const [loadPercent, setLoadPercent] = useState(0);

    const loadDxf = async (url) => {
        if (!viewerRef.current) return;
        setIsLoading(true);
        try {
            await viewerRef.current.Load({
                url,
                progressCbk: (phase, processed, total) => {
                    if (phase === 'fetch' && total) {
                        setLoadPercent(Math.round((processed / total) * 100));
                    }
                }
            });
            const layerData = viewerRef.current.GetLayers(true);
            setLayers(layerData);
            setIsLoading(false);
            
            const bounds = viewerRef.current.GetBounds();
            if (bounds) {
                viewerRef.current.FitView(bounds.minX, bounds.maxX, bounds.minY, bounds.maxY, 0.1);
            }
        } catch (err) {
            console.error("Failed to load DXF:", err);
            setIsLoading(false);
        }
    };

    const applyTheme = (themeName) => {
        if (!viewerRef.current) return;
        const color = themeName === 'store' ? new THREE.Color("#ffffff") : new THREE.Color("#000000");
        viewerRef.current.GetRenderer().setClearColor(color, 0); // Background is still transparent (alpha 0)
        setTheme(themeName);
    };

    useEffect(() => {
        if (!containerRef.current) return;

        const viewer = new DxfViewer(containerRef.current, {
            autoResize: true,
            clearColor: new THREE.Color("#000000"),
            clearAlpha: 0, // Make background transparent
            antialias: true,
            colorCorrection: true,
            blackWhiteInversion: true, // Automatically invert colors for light/dark
            sceneOptions: {
                arcTessellationAngle: 2 * Math.PI / 180,
            }
        });

        viewerRef.current = viewer;

        const onPointerMove = (e) => {
            const { position } = e.detail;
            if (position) {
                setCoords({ x: position.x.toFixed(4), y: position.y.toFixed(4) });
            }
        };

        viewer.Subscribe('pointermove', onPointerMove);

        loadDxf(currentFile);

        // Add a floor grid if in Store mode - we'll handle this in a separate effect or toggle
        
        return () => {
            viewer.Destroy();
        };
    }, []);

    useEffect(() => {
        if (viewerRef.current && currentFile) {
            loadDxf(currentFile);
        }
    }, [currentFile]);

    const toggleLayer = (layerName) => {
        if (!viewerRef.current) return;
        const layer = layers.find(l => l.name === layerName);
        if (layer) {
            const visible = !viewerRef.current.IsLayerVisible(layerName);
            viewerRef.current.SetLayerVisibility(layerName, visible);
            setLayers([...viewerRef.current.GetLayers(true)]);
        }
    };

    const handleFitView = () => {
        if (!viewerRef.current) return;
        const bounds = viewerRef.current.GetBounds();
        if (bounds) {
            viewerRef.current.FitView(bounds.minX, bounds.maxX, bounds.minY, bounds.maxY, 0.1);
        }
    };

    return (
        <div className={`app-container ${theme}-theme`}>
            {isLoading && (
                <div className="loading-overlay">
                    <div className="spinner"></div>
                    <div className="loading-text">Optimizing Store Floor Plan... {loadPercent}%</div>
                </div>
            )}

            <div id="cad-container" ref={containerRef}></div>

            <div className="header-overlay">
                <div className="title-card">
                    <h1>RETAIL BLUEPRINT ENGINE</h1>
                    <div className="controls">
                        <select 
                            className="btn" 
                            style={{ background: '#1c2128', border: '1px solid #30363d' }}
                            value={currentFile}
                            onChange={(e) => setCurrentFile(e.target.value)}
                        >
                            <option value="/floor_plan.dxf">Hyperlink Market Plan</option>
                            <option value="/sample.dxf">Basic Shapes</option>
                        </select>
                        <button className="btn" onClick={() => applyTheme(theme === 'dark' ? 'store' : 'dark')}>
                            {theme === 'dark' ? 'Enable Store View' : 'Enable Dark Mode'}
                        </button>
                        <button className="btn" onClick={handleFitView}>Center View</button>
                    </div>
                </div>
            </div>

            <aside className="sidebar">
                <h2>
                    <span style={{ fontSize: '1rem' }}>Layers</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 'normal' }}>
                        ({layers.length})
                    </span>
                </h2>
                <ul className="layer-list">
                    {layers.map((layer) => (
                        <li 
                            key={layer.name} 
                            className="layer-item"
                            onClick={() => toggleLayer(layer.name)}
                            style={{ opacity: layer.visible ? 1 : 0.5 }}
                        >
                            <div 
                                className="layer-color" 
                                style={{ backgroundColor: `#${layer.color.toString(16).padStart(6, '0')}` }}
                            ></div>
                            <span className="layer-name">{layer.displayName || layer.name}</span>
                            <input 
                                type="checkbox" 
                                readOnly 
                                checked={layer.visible} 
                                className="layer-toggle" 
                            />
                        </li>
                    ))}
                </ul>
            </aside>

            <footer className="status-bar">
                <div className="status-left">
                    Status: <span style={{ color: '#50fa7b' }}>Ready</span>
                </div>
                <div className="coords">
                    X: {coords.x} / Y: {coords.y}
                </div>
                <div className="status-right">
                    Three.js + DxfViewer
                </div>
            </footer>
        </div>
    );
};

export default App;
