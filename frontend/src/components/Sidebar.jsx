import React from 'react';
import { LayoutDashboard, FolderKanban, FileText, Calendar, Users, Settings, Rocket, LogOut, Image, Globe } from 'lucide-react';

const Sidebar = () => {
    const user = window.django?.user;
    const allowed = window.django?.allowed_tools || [];
    const isAdmin = user?.is_superuser;

    const allNavItems = [
        ...(isAdmin ? [{ icon: LayoutDashboard, label: 'Admin Dashboard', url: '/dashboard/' }] : []),
        { icon: FolderKanban, label: 'Projects', slug: 'projects' }, // Assuming 'projects' tool
        { icon: FileText, label: 'Documents', url: '/documents/', slug: 'documents' },
        { icon: Image, label: 'Image Compressor', url: '/tools/compressor/', slug: 'image-compressor' },
        { icon: Globe, label: '3D Viewer', url: '/3d/', slug: '3d-view' },
        { icon: Calendar, label: 'Calendar', slug: 'calendar' }, // Assuming 'calendar' tool
        { icon: Users, label: 'Team', slug: 'team' }, // Assuming 'team' tool
        { icon: Settings, label: 'Settings', url: '/profile/' }, // Profile is usually generic
    ];

    const navItems = allNavItems.filter(item => {
        if (isAdmin) return true;
        // Always show Settings or items without slugs (if any intended to be public)
        // Also always show 'documents' as requested
        if (!item.slug || item.slug === 'documents') return true;
        return allowed.includes(item.slug);
    });

    const handleNavigation = (url, e) => {
        if (url) {
            e.preventDefault();
            window.location.href = url;
        }
    };

    return (
        <div className="w-64 h-screen bg-slate-950 border-r border-slate-800 flex flex-col fixed left-0 top-0 z-50">
            <div className="p-6 flex items-center gap-3 border-b border-slate-800/50">
                <div className="w-8 h-8 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <Rocket className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                    Office Portal
                </span>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto custom-scrollbar">
                {navItems.map((item, index) => (
                    <a
                        key={index}
                        href={item.url || '#'}
                        onClick={(e) => handleNavigation(item.url, e)}
                        className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-900 rounded-xl transition-all duration-200 group cursor-pointer"
                    >
                        <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
                        <span className="font-medium">{item.label}</span>
                    </a>
                ))}
            </nav>

            <div className="px-4 py-2 border-t border-slate-800/50 bg-slate-950">
                <a
                    href="/logout/"
                    onClick={(e) => {
                        e.preventDefault();
                        window.location.href = "/logout/";
                    }}
                    className="flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-all duration-200 group cursor-pointer mb-2"
                >
                    <LogOut className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
                    <span className="font-medium">Logout</span>
                </a>

                <div className="p-4 rounded-xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800">
                    <p className="text-xs text-slate-400">Logged in as</p>
                    <p className="text-sm font-semibold text-white truncate" title={window.django?.user?.full_name}>
                        {window.django?.user?.full_name || 'User'}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
