import React from 'react';
import { LayoutDashboard, FolderKanban, FileText, Calendar, Users, Settings, Rocket } from 'lucide-react';

const Sidebar = () => {
    const isAdmin = window.django?.user?.is_superuser;

    const navItems = [
        ...(isAdmin ? [{ icon: LayoutDashboard, label: 'Admin Dashboard', url: '/dashboard/' }] : []),
        { icon: FolderKanban, label: 'Projects' },
        { icon: FileText, label: 'Documents' },
        { icon: Calendar, label: 'Calendar' },
        { icon: Users, label: 'Team' },
        { icon: Settings, label: 'Settings' },
    ];

    return (
        <div className="w-64 h-screen bg-slate-950 border-r border-slate-800 flex flex-col fixed left-0 top-0">
            <div className="p-6 flex items-center gap-3 border-b border-slate-800/50">
                <div className="w-8 h-8 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <Rocket className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                    Office Portal
                </span>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map((item, index) => (
                    <a
                        key={index}
                        href={item.url || '#'}
                        className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-900 rounded-xl transition-all duration-200 group"
                    >
                        <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
                        <span className="font-medium">{item.label}</span>
                    </a>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-800/50">
                <div className="p-4 rounded-xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800">
                    <p className="text-xs text-slate-400">Logged in as</p>
                    <p className="text-sm font-semibold text-white">{window.django?.user?.full_name || 'User'}</p>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
