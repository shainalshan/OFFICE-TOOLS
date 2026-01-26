import React, { useState, useEffect, useRef } from 'react';
import { Search, Bell, Calendar as CalendarIcon, ChevronDown } from 'lucide-react';
import { getCookie } from '../utils/csrf';

const Header = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const dropdownRef = useRef(null);
    const bellRef = useRef(null);

    // Fetch initial state and poll
    useEffect(() => {
        const fetchUnreadCount = async () => {
            try {
                const timestamp = new Date().getTime();
                const res = await fetch(`/api/notifications/check/?t=${timestamp}`, { credentials: 'include' });
                if (res.ok) {
                    const data = await res.json();
                    setUnreadCount(data.unread_count);
                }
            } catch (err) {
                console.error("Failed to check notifications", err);
            }
        };

        fetchUnreadCount();
        const interval = setInterval(fetchUnreadCount, 10000); // Poll every 10s

        // Click outside listener
        const handleClickOutside = (event) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target) &&
                bellRef.current &&
                !bellRef.current.contains(event.target)
            ) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            clearInterval(interval);
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const fetchNotifications = async (page = 1) => {
        setLoading(true);
        try {
            const timestamp = new Date().getTime();
            const res = await fetch(`/api/notifications/list/?page=${page}&t=${timestamp}`, { credentials: 'include' });
            if (res.ok) {
                const data = await res.json();
                setNotifications(data.notifications);
            }
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        } finally {
            setLoading(false);
        }
    };

    const toggleNotifications = (e) => {
        // Prevent event bubbling which might trigger outside click immediately
        e.preventDefault();
        e.stopPropagation();

        console.log('Toggle notifications clicked. Current State:', isOpen);

        if (!isOpen) {
            fetchNotifications();
            setIsOpen(true);
        } else {
            setIsOpen(false);
        }
    };

    const markRead = async (e, id) => {
        e.stopPropagation();
        try {
            const res = await fetch(`/api/notifications/mark-read/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });
            const data = await res.json();
            if (data.status === 'success') {
                fetchNotifications();
                setUnreadCount(prev => Math.max(0, prev - 1));
            }
        } catch (err) {
            console.error("Error marking read", err);
        }
    };

    const markUnread = async (e, id) => {
        e.stopPropagation();
        try {
            const res = await fetch(`/api/notifications/mark-unread/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });
            const data = await res.json();
            if (data.status === 'success') {
                fetchNotifications();
                setUnreadCount(prev => prev + 1);
            }
        } catch (err) {
            console.error("Error marking unread", err);
        }
    };

    const deleteNotification = async (e, id) => {
        e.stopPropagation();
        try {
            const res = await fetch(`/api/notifications/delete/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });
            const data = await res.json();
            if (data.status === 'success') {
                fetchNotifications();
            }
        } catch (err) {
            console.error("Error deleting", err);
        }
    };

    const markAllRead = async (e) => {
        e.stopPropagation();
        try {
            await fetch('/api/notifications/mark-all-read/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            fetchNotifications();
            setUnreadCount(0);
        } catch (err) { console.error(err); }
    };

    const markAllUnread = async (e) => {
        e.stopPropagation();
        try {
            await fetch('/api/notifications/mark-all-unread/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            fetchNotifications();
            // Re-check count to be accurate
            const res = await fetch(`/api/notifications/check/?t=${Date.now()}`, { credentials: 'include' });
            if (res.ok) {
                const data = await res.json();
                setUnreadCount(data.unread_count);
            }
        } catch (err) { console.error(err); }
    };

    const clearAll = async (e) => {
        e.stopPropagation();
        try {
            await fetch('/api/notifications/clear-all/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            setNotifications([]);
            setUnreadCount(0);
        } catch (err) { console.error(err); }
    };

    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const formatTime = (date) => {
        let hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        const strMinutes = minutes < 10 ? '0' + minutes : minutes;
        return `${hours}:${strMinutes} ${ampm}`;
    };

    return (
        <header className="h-20 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/50 flex items-center justify-between px-8 fixed top-0 left-64 right-0 z-50 transition-all duration-300">
            <div className="relative w-96 font-sans">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                    type="text"
                    placeholder="Search tools, projects, documents..."
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                />
            </div>

            <div className="flex items-center gap-6">
                <div className="text-sm font-medium text-slate-200" style={{ fontVariantNumeric: 'tabular-nums' }}>
                    {formatTime(currentTime)}
                </div>

                <button className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                    <CalendarIcon className="w-5 h-5" />
                </button>

                {/* Notification Bell */}
                <div className="relative">
                    <button
                        ref={bellRef}
                        onClick={toggleNotifications}
                        className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        <Bell className="w-5 h-5" />
                        {unreadCount > 0 && (
                            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-slate-950"></span>
                        )}
                    </button>

                    {/* Dropdown */}
                    {isOpen && (
                        <div
                            ref={dropdownRef}
                            className="absolute right-0 top-full mt-2 w-80 overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-xl z-50 text-left"
                            style={{ minWidth: '320px' }}
                        >
                            {/* Header */}
                            <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900">
                                <span className="text-xs text-slate-400">Recent</span>
                                <div className="flex gap-3">
                                    <button onClick={markAllUnread} className="text-xs text-amber-500 cursor-pointer hover:underline bg-transparent border-0 p-0">Unread</button>
                                    <button onClick={markAllRead} className="text-xs text-blue-500 cursor-pointer hover:underline bg-transparent border-0 p-0">Read</button>
                                    <button onClick={clearAll} className="text-xs text-red-500 cursor-pointer hover:underline bg-transparent border-0 p-0">Clear</button>
                                </div>
                            </div>

                            {/* List */}
                            <div className="max-h-96 overflow-y-auto custom-scrollbar bg-slate-900">
                                {loading && <div className="p-4 text-center text-sm text-slate-400">Loading...</div>}
                                {!loading && notifications.length === 0 && (
                                    <div className="p-4 text-center text-sm text-slate-400">No notifications</div>
                                )}
                                {!loading && notifications.map(n => (
                                    <div
                                        key={n.id}
                                        onClick={() => { if (n.link && n.link !== '#') window.location.href = n.link; }}
                                        className={`p-3 border-b border-slate-800 relative transition-colors hover:bg-slate-800 cursor-pointer ${n.is_read ? 'bg-transparent' : 'bg-indigo-500/10'}`}
                                    >
                                        <div className="absolute top-2 right-2 flex gap-2">
                                            {n.is_read ? (
                                                <button title="Mark as Unread" onClick={(e) => markUnread(e, n.id)} className="cursor-pointer text-xs text-slate-500 hover:text-white bg-transparent border-0 p-0">⭕</button>
                                            ) : (
                                                <button title="Mark as Read" onClick={(e) => markRead(e, n.id)} className="cursor-pointer text-xs text-blue-500 hover:text-blue-400 bg-transparent border-0 p-0">●</button>
                                            )}
                                            <button title="Clear" onClick={(e) => deleteNotification(e, n.id)} className="cursor-pointer text-xs text-red-500 hover:text-red-400 bg-transparent border-0 p-0">✕</button>
                                        </div>
                                        <div className="mr-8">
                                            <div className={`font-medium text-sm text-slate-200 mb-1 ${!n.is_read ? 'font-semibold' : ''}`}>{n.title}</div>
                                            <div className="text-xs text-slate-400 leading-relaxed">{n.message}</div>
                                            <div className="text-[10px] text-slate-500 mt-2">{n.created_at}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-3 pl-6 border-l border-slate-800">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-sm font-bold text-white shadow-lg ring-2 ring-slate-800">
                        {(window.django?.user?.username || 'U').substring(0, 2).toUpperCase()}
                    </div>
                    <div className="flex items-center gap-2 cursor-pointer group">
                        <span className="text-sm font-medium text-slate-200 group-hover:text-white">
                            {window.django?.user?.username || 'User'}
                        </span>
                        <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-white transition-transform group-hover:rotate-180" />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
