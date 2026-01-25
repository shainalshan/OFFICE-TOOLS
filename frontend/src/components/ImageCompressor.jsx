import React, { useState, useEffect } from 'react';

const ImageCompressor = () => {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [csrfToken, setCsrfToken] = useState('');
    const [error, setError] = useState('');
    const [previewUrl, setPreviewUrl] = useState(null);

    useEffect(() => {
        // Get CSRF token from cookie
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
    }, []);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (selectedFile) => {
        setError('');
        if (selectedFile.size > 5 * 1024 * 1024) {
            setError('File size too large. Max allowed size is 5MB.');
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        if (!selectedFile.type.startsWith('image/')) {
            setError('Please select a valid image file.');
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        setFile(selectedFile);
        const url = URL.createObjectURL(selectedFile);
        setPreviewUrl(url);
    };

    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [previewUrl]);

    return (
        <div className="animate-fade-in">
            <div className="max-w-3xl mx-auto">
                <div className="text-center mb-8 space-y-2">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
                        Image Compressor
                    </h1>
                    <p className="text-slate-400">
                        Compress your images efficiently. Target size: 30-50KB.
                    </p>
                </div>

                <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl p-8 shadow-xl">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-200 px-4 py-3 rounded-xl mb-6 flex items-center gap-2">
                            <span className="text-xl">⚠️</span> {error}
                        </div>
                    )}

                    <form
                        action="/tools/compressor/"
                        method="POST"
                        encType="multipart/form-data"
                        className="space-y-8"
                    >
                        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

                        <div
                            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${dragActive
                                    ? 'border-blue-500 bg-blue-500/10 scale-[1.02]'
                                    : 'border-slate-700 hover:border-slate-600 hover:bg-slate-800/30'
                                }`}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                name="image"
                                id="file-upload"
                                className="hidden"
                                accept="image/*"
                                onChange={handleChange}
                            />

                            <label htmlFor="file-upload" className="cursor-pointer block">
                                <div className="text-6xl mb-4">🖼️</div>
                                <h3 className="text-xl font-semibold text-white mb-2">
                                    {file ? 'Change Image' : 'Click or Drag Image Here'}
                                </h3>
                                <p className="text-slate-400 text-sm">
                                    Supported formats: JPG, PNG. Max size: 5MB
                                </p>
                            </label>
                        </div>

                        {file && (
                            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center gap-4 animate-fade-in">
                                {previewUrl && (
                                    <div className="w-16 h-16 rounded-lg overflow-hidden border border-slate-700">
                                        <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                                    </div>
                                )}
                                <div className="flex-1 min-w-0">
                                    <p className="text-white font-medium truncate">{file.name}</p>
                                    <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                                <div className="text-blue-400 font-semibold text-sm">Ready</div>
                            </div>
                        )}

                        <div className="pt-4">
                            <button
                                type="submit"
                                disabled={!file}
                                className={`w-full py-4 px-6 rounded-xl shadow-lg transform transition-all duration-200 font-bold text-white
                                    ${file
                                        ? 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 hover:scale-[1.02] active:scale-[0.98] cursor-pointer'
                                        : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                                    }`}
                            >
                                Compress & Download ⬇️
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ImageCompressor;
