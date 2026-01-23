import React, { useState, useEffect } from 'react';

const SignatureGenerator = () => {
    const [formData, setFormData] = useState({
        signature_model: 'pixl',
        name: '',
        designation: '',
        email: '',
        phone_mobile: '',
        phone_office: '+971 45572884',
        website: 'www.pixl.ae',
        address: '38th Floor, Al Habtoor Business Tower, King Salman Bin Abdulaziz Al Saud St, Dubai Marina, Dubai, UAE',
        calendar_link: ''
    });

    const [csrfToken, setCsrfToken] = useState('');

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

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => {
            const newData = { ...prev, [name]: value };

            // Handle preset defaults based on model
            if (name === 'signature_model') {
                if (value === 'invespy') {
                    newData.website = 'www.invespy.com';
                    newData.address = '1903, Swiss Tower, JLT, Dubai';
                } else if (value && value.startsWith('pixl')) {
                    newData.website = 'www.pixl.ae';
                    newData.address = '38th Floor, Al Habtoor Business Tower, King Salman Bin Abdulaziz Al Saud St, Dubai Marina, Dubai, UAE';
                }
            }
            return newData;
        });
    };

    return (
        <div className="ml-64 pt-20 min-h-screen p-8 bg-slate-950 text-white">
            <div className="max-w-3xl mx-auto">
                <div className="text-center mb-8 space-y-2">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-orange-500">
                        Create Your Signature
                    </h1>
                    <p className="text-slate-400">
                        Enter your details below to generate a professional HTML signature.
                    </p>
                </div>

                <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl p-8 shadow-xl">
                    <form action="/signature/" method="POST" encType="multipart/form-data" className="space-y-6">
                        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Signature Model</label>
                            <select
                                name="signature_model"
                                value={formData.signature_model}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                            >
                                <option value="pixl">Pixl Email Signature</option>
                                <option value="pixl_calendar">Pixl Email Signature - with Calendar</option>
                                <option value="invespy">Invespy Email Signature</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Full Name</label>
                            <input
                                type="text"
                                name="name"
                                required
                                placeholder="e.g. John Doe"
                                value={formData.name}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Designation</label>
                            <input
                                type="text"
                                name="designation"
                                required
                                placeholder="e.g. Software Engineer"
                                value={formData.designation}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Email Address</label>
                            <input
                                type="email"
                                name="email"
                                required
                                placeholder="john@company.com"
                                value={formData.email}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Mobile Number</label>
                                <input
                                    type="tel"
                                    name="phone_mobile"
                                    required
                                    placeholder="+971 50..."
                                    value={formData.phone_mobile}
                                    onChange={handleChange}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Office Number</label>
                                <input
                                    type="tel"
                                    name="phone_office"
                                    placeholder="+971 4..."
                                    value={formData.phone_office}
                                    onChange={handleChange}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Website</label>
                            <input
                                type="text"
                                name="website"
                                value={formData.website}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Address</label>
                            <input
                                type="text"
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                            />
                        </div>

                        {formData.signature_model === 'pixl_calendar' && (
                            <div className="space-y-2 animate-fade-in">
                                <label className="text-sm font-medium text-slate-300">Calendar Link</label>
                                <input
                                    type="url"
                                    name="calendar_link"
                                    required
                                    placeholder="https://calendly.com/your-name"
                                    value={formData.calendar_link}
                                    onChange={handleChange}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all"
                                />
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Profile Photo (Max 50KB)</label>
                            <div className="relative">
                                <input
                                    type="file"
                                    name="photo"
                                    required
                                    accept="image/*"
                                    className="w-full file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-orange-500 file:text-white hover:file:bg-orange-600 bg-slate-950 border border-slate-700 rounded-xl text-slate-300 focus:outline-none transition-all cursor-pointer"
                                />
                            </div>
                            <p className="text-xs text-slate-500">Supported formats: JPG, PNG. Image will be automatically resized.</p>
                        </div>

                        <div className="pt-4">
                            <button
                                type="submit"
                                className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-4 px-6 rounded-xl shadow-lg transform transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                            >
                                Generate Signature
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default SignatureGenerator;
