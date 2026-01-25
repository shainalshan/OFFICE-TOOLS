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
        <div className="space-y-8 animate-fade-in">
            <div className="relative z-10 w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl p-5 shadow-2xl overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl"></div>
                <div className="relative flex flex-col gap-1">
                    <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                        Welcome, {window.django?.user?.full_name || 'User'}!
                    </h1>
                    <p className="text-blue-100 text-sm font-medium opacity-90">
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
        </div>
    );
};

export default Dashboard;
