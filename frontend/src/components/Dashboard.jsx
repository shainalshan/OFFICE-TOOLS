import React from 'react';
import ToolCard from './ToolCard';

const Dashboard = () => {
    const tools = [
        {
            title: 'Signature Generator',
            description: 'Create professional email signatures',
            icon: '✍️',
            color: 'from-yellow-400 to-orange-500',
            url: '/signature/'
        },
        {
            title: 'IT Support Tickets',
            description: 'Submit support requests',
            icon: '🎫',
            color: 'from-amber-300 to-yellow-500',
            url: '/tickets/'
        },
        {
            title: 'Asset Manager',
            description: 'Track office inventory',
            icon: '📦',
            color: 'from-orange-400 to-red-500',
            url: '/assets/'
        },
        {
            title: 'Office News',
            description: 'Announcements & Updates',
            icon: '📢',
            color: 'from-pink-500 to-rose-500',
            url: '/news/'
        },
        {
            title: 'System Monitor',
            description: 'Server health metrics',
            icon: '📊',
            color: 'from-green-400 to-emerald-500',
            url: '/monitor/'
        },
        {
            title: 'Contact Manager',
            description: 'Shared office contacts',
            icon: '👥',
            color: 'from-purple-500 to-indigo-500',
            url: '/contacts/'
        },
        {
            title: 'Group Chat',
            description: 'Team collaboration',
            icon: '💬',
            color: 'from-blue-400 to-indigo-500',
            url: '/tools/chat/'
        },
        {
            title: 'PDF to Word',
            description: 'Convert PDF documents',
            icon: '📄',
            color: 'from-red-400 to-red-600',
            url: '/tools/pdf-to-word/'
        },
        {
            title: 'Image Compressor',
            description: 'Optimize image sizes',
            icon: '🖼️',
            color: 'from-teal-400 to-emerald-500',
            url: '/tools/compressor/'
        },
        {
            title: '3D Viewer',
            description: 'View 3D models',
            icon: '🧊',
            color: 'from-violet-400 to-fuchsia-500',
            url: '/3d/'
        },
        {
            title: 'Device Tracker',
            description: 'Track assigned devices',
            icon: '📍',
            color: 'from-cyan-400 to-blue-500',
            url: '/tracker/'
        },
        {
            title: 'Background Remover',
            description: 'Remove image backgrounds',
            icon: '✂️',
            color: 'from-gray-400 to-slate-500',
            url: '/tools/background-remover/'
        },
        {
            title: 'File Converter',
            description: 'Convert file formats',
            icon: '🔄',
            color: 'from-orange-400 to-amber-500',
            url: '/tools/converter/'
        },
        {
            title: 'Backup & Restore',
            description: 'System backups',
            icon: '💾',
            color: 'from-emerald-400 to-green-600',
            url: '/backup/'
        },
        {
            title: 'PIXL AI',
            description: 'AI Image Tools',
            icon: '✨',
            color: 'from-indigo-400 to-purple-600',
            url: '/pixl_ai/'
        }
    ];

    return (
        <main className="ml-64 pt-20 min-h-screen p-8 space-y-8 bg-slate-950 text-white relative overflow-hidden">
            {/* Background elements */}
            <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden -z-0">
                <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-3xl opacity-50"></div>
                <div className="absolute bottom-[-10%] left-[20%] w-[400px] h-[400px] bg-blue-900/20 rounded-full blur-3xl opacity-50"></div>
            </div>

            <div className="relative z-10 w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl p-10 shadow-2xl overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl"></div>
                <div className="relative flex flex-col gap-2">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">
                        Welcome, shainal badusha!
                    </h1>
                    <p className="text-blue-100 text-lg font-medium opacity-90">
                        Here are your essential tools.
                    </p>
                </div>
            </div>

            <div className="relative z-10 space-y-6">
                <div className="text-center space-y-2 py-4">
                    <h2 className="text-2xl font-bold text-white">Select a Tool</h2>
                    <div className="w-16 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto rounded-full"></div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {tools.map((tool, index) => (
                        <a key={index} href={tool.url || '#'}>
                            <ToolCard {...tool} />
                        </a>
                    ))}
                </div>
            </div>
        </main>
    );
};

export default Dashboard;
