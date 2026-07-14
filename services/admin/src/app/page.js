'use client';

import React, { useState, useEffect } from 'react';

// ============================================================================
// INITIAL MOCK DATABASE (REPRESENTING BACKEND SCHEMA MODELS)
// ============================================================================
const initialUsers = [
  { id: 1, email: 'john.barber@hairlync.com', full_name: 'John Cutts', role: 'barber', is_verified: true, is_active: true, date_joined: '2026-02-14', plan: 'monthly', is_sub_profile: false, business_name: 'Elite Barbering Studio', rating: 4.85, total_bookings: 342 },
  { id: 2, email: 'alex.client@gmail.com', full_name: 'Alex Johnson', role: 'client', is_verified: true, is_active: true, date_joined: '2026-05-10', plan: 'free', is_sub_profile: false, business_name: '', rating: 0, total_bookings: 14 },
  { id: 3, email: 'admin@hairlync.com', full_name: 'Platform Admin', role: 'admin', is_verified: true, is_active: true, date_joined: '2026-01-01', plan: 'free', is_sub_profile: false, business_name: '', rating: 0, total_bookings: 0 },
  { id: 4, email: 'sophie.stylist@hairlync.app', full_name: 'Sophie Dubois', role: 'salon', is_verified: true, is_active: true, date_joined: '2026-04-18', plan: 'free', is_sub_profile: true, parent_salon: 'luxe-salon', business_name: 'Luxe Hair Salon', rating: 4.91, total_bookings: 188 },
  { id: 5, email: 'luxe.salon@hairlync.com', full_name: 'Luxe Hair Salon', role: 'salon', is_verified: false, is_active: true, date_joined: '2026-03-01', plan: 'yearly', is_sub_profile: false, business_name: 'Luxe Salon HQ', rating: 4.67, total_bookings: 540 },
  { id: 6, email: 'marcus.fade@hairlync.com', full_name: 'Marcus Lopez', role: 'barber', is_verified: false, is_active: true, date_joined: '2026-05-20', plan: 'free', is_sub_profile: false, business_name: 'Fades & Shades', rating: 4.20, total_bookings: 48 },
  { id: 7, email: 'anna.stylist@hairlync.app', full_name: 'Anna Kendrick', role: 'salon', is_verified: true, is_active: true, date_joined: '2026-05-22', plan: 'free', is_sub_profile: true, parent_salon: 'luxe-salon', business_name: 'Luxe Hair Salon', rating: 4.75, total_bookings: 96 }
];

const initialBookings = [
  { id: 101, client: 'Alex Johnson', provider: 'Elite Barbering Studio', service: 'Classic Fade & Beard Trim', date: '2026-06-06', time: '14:30', status: 'approved', price: '$45.00' },
  { id: 102, client: 'David Miller', provider: 'Luxe Hair Salon (Sophie Dubois)', service: 'Balayage & Hair Treatment', date: '2026-06-06', time: '16:00', status: 'pending', price: '$120.00' },
  { id: 103, client: 'Sarah Connor', provider: 'Fades & Shades', service: 'Pixie Haircut', date: '2026-06-07', time: '10:00', status: 'pending', price: '$35.00' },
  { id: 104, client: 'James Carter', provider: 'Elite Barbering Studio', service: 'Hot Towel Shave', date: '2026-06-05', time: '11:15', status: 'completed', price: '$30.00' },
  { id: 105, client: 'Michael Scott', provider: 'Luxe Hair Salon (Anna Kendrick)', service: 'Men\'s Hair Styling', date: '2026-06-04', time: '09:30', status: 'cancelled', price: '$40.00', cancellation_reason: 'Client rescheduled' }
];

const initialReviews = [
  { id: 201, client: 'Alex Johnson', provider: 'Elite Barbering Studio', rating: 5, comment: 'Hands down the best fade in the city. Clean shop and extremely professional staff!', is_approved: true, is_flagged: false },
  { id: 202, client: 'David Miller', provider: 'Fades & Shades', rating: 2, comment: 'The haircut was rushed. My sideburns are completely uneven.', is_approved: true, is_flagged: false },
  { id: 203, client: 'Robert Downey', provider: 'Luxe Salon HQ', rating: 1, comment: 'Horrible service! Scammed me on the pricing! Avoid this place, absolute scammers!', is_approved: false, is_flagged: true, flag_reason: 'Contains offensive/abusive language' }
];

const initialAiRecommendations = [
  { id: 301, client: 'Alex Johnson', provider: 'Elite Barbering Studio', image: '/placeholder_client1.jpg', hair_length: 'medium', status: 'pending', date: '2026-06-05', notes: 'Looking for a fresh summer hairstyle that fits an oval face structure.', recommended_style: '' },
  { id: 302, client: 'Sarah Connor', provider: 'Luxe Hair Salon', image: '/placeholder_client2.jpg', hair_length: 'long', status: 'completed', date: '2026-06-04', notes: 'Wants a low-maintenance formal hairstyle.', recommended_style: 'Textured Shag Cut with Soft Layering' }
];

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  // Dashboard Database States
  const [users, setUsers] = useState(initialUsers);
  const [bookings, setBookings] = useState(initialBookings);
  const [reviews, setReviews] = useState(initialReviews);
  const [aiItems, setAiItems] = useState(initialAiRecommendations);

  // Filter States
  const [userRoleFilter, setUserRoleFilter] = useState('all');
  const [bookingStatusFilter, setBookingStatusFilter] = useState('all');
  const [reviewFilter, setReviewFilter] = useState('all');

  // Modal States
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [selectedReview, setSelectedReview] = useState(null);
  const [selectedAi, setSelectedAi] = useState(null);

  // Action Feedback Toast
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  // Simulated AI Engine Processing State
  const [analyzingId, setAnalyzingId] = useState(null);

  // Trigger Toast Notification Helper
  const triggerToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
  };

  useEffect(() => {
    if (toast.show) {
      const timer = setTimeout(() => {
        setToast({ show: false, message: '', type: 'success' });
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [toast.show]);

  // Core Backend Handler Mock Simulations
  const handleToggleVerifyUser = (id) => {
    const updated = users.map(user => {
      if (user.id === id) {
        const nextState = !user.is_verified;
        triggerToast(`${user.full_name} is now ${nextState ? 'Verified' : 'Unverified'}.`, 'success');
        return { ...user, is_verified: nextState };
      }
      return user;
    });
    setUsers(updated);
    if (selectedUser && selectedUser.id === id) {
      setSelectedUser({ ...selectedUser, is_verified: !selectedUser.is_verified });
    }
  };

  const handleToggleActiveUser = (id) => {
    const updated = users.map(user => {
      if (user.id === id) {
        const nextState = !user.is_active;
        triggerToast(`${user.full_name} is now ${nextState ? 'Active' : 'Suspended'}.`, nextState ? 'success' : 'warning');
        return { ...user, is_active: nextState };
      }
      return user;
    });
    setUsers(updated);
    if (selectedUser && selectedUser.id === id) {
      setSelectedUser({ ...selectedUser, is_active: !selectedUser.is_active });
    }
  };

  const handleDeleteUser = (id) => {
    const targetUser = users.find(u => u.id === id);
    if (!targetUser) return;

    // Enforce Backend Sub-Profile Restrictions
    if (targetUser.role === 'salon' && targetUser.is_sub_profile) {
      triggerToast('Security Error: Sub-profile employees cannot be deleted directly by platform admins. They must be managed by the Salon owner.', 'danger');
      return;
    }

    if (confirm(`Are you sure you want to delete user ${targetUser.email}?`)) {
      setUsers(users.filter(u => u.id !== id));
      setSelectedUser(null);
      triggerToast('User account successfully deleted.', 'success');
    }
  };

  const handleBookingStatus = (id, newStatus) => {
    const updated = bookings.map(b => {
      if (b.id === id) {
        triggerToast(`Booking #${id} status changed to ${newStatus.toUpperCase()}.`, 'success');
        return { ...b, status: newStatus };
      }
      return b;
    });
    setBookings(updated);
    if (selectedBooking && selectedBooking.id === id) {
      setSelectedBooking({ ...selectedBooking, status: newStatus });
    }
  };

  const handleReviewAction = (id, action) => {
    const updated = reviews.map(r => {
      if (r.id === id) {
        if (action === 'approve') {
          triggerToast('Review approved for public display.', 'success');
          return { ...r, is_approved: true, is_flagged: false, flag_reason: '' };
        } else if (action === 'flag') {
          triggerToast('Review flagged for content violation.', 'warning');
          return { ...r, is_flagged: true, is_approved: false };
        } else if (action === 'delete') {
          triggerToast('Review permanently deleted.', 'success');
          return null;
        }
      }
      return r;
    }).filter(Boolean);

    setReviews(updated);
    setSelectedReview(null);
  };

  const handleRunAIRecommendation = (id) => {
    setAnalyzingId(id);
    triggerToast('Sending portrait to Hairlync AI engine (Google Studio/OpenAI API fallback)...', 'success');

    setTimeout(() => {
      const styles = [
        'Modern Textured Pompadour with Skin Fade',
        'Mid-Length Layered Flow with Low Highlight',
        'Classic High & Tight Fade with Line Up',
        'Subtle Undercut with Textured Crop Top',
        'Naturally Sculpted Coils with Tapered Sides'
      ];
      const randomStyle = styles[Math.floor(Math.random() * styles.length)];

      const updated = aiItems.map(item => {
        if (item.id === id) {
          return { ...item, status: 'completed', recommended_style: randomStyle };
        }
        return item;
      });
      setAiItems(updated);
      setAnalyzingId(null);
      triggerToast(`AI Styling analysis complete! Suggested: ${randomStyle}`, 'success');
      if (selectedAi && selectedAi.id === id) {
        setSelectedAi({ ...selectedAi, status: 'completed', recommended_style: randomStyle });
      }
    }, 3000);
  };

  // Dashboard Stats
  const stats = {
    totalUsers: users.length,
    activeBarbers: users.filter(u => u.role === 'barber' && u.is_active).length,
    activeSalons: users.filter(u => u.role === 'salon' && !u.is_sub_profile && u.is_active).length,
    mrr: '$14,240',
    pendingBookings: bookings.filter(b => b.status === 'pending').length,
    flaggedReviews: reviews.filter(r => r.is_flagged).length,
    aiAccuracy: '98.6%',
    apiLatency: '112ms'
  };

  return (
    <div className="admin-container">
      {/* GLOBAL CSS STYLING INJECTED TO SUPPORT KEYFRAMES, SCROLLBARS, AND RESPONSIVENESS */}
      <style dangerouslySetInnerHTML={{
        __html: `
        :root {
          --bg-primary: #0d1117;
          --bg-secondary: #161b22;
          --bg-card: #21262d;
          --border: #30363d;
          --text-main: #c9d1d9;
          --text-sec: #8b949e;
          --blue: #58a6ff;
          --indigo: #6f42c1;
          --emerald: #3fb950;
          --amber: #d29922;
          --red: #f85149;
          --glass-bg: rgba(22, 27, 34, 0.7);
        }

        body {
          margin: 0;
          background-color: var(--bg-primary);
          color: var(--text-main);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          overflow-x: hidden;
        }

        .admin-container {
          display: flex;
          min-height: 100vh;
        }

        /* Sidebar Navigation */
        .sidebar {
          width: 260px;
          background-color: var(--bg-secondary);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          padding: 1.5rem 1rem;
          box-sizing: border-box;
          position: fixed;
          height: 100vh;
          z-index: 100;
        }

        .logo-section {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 2rem;
          padding-left: 0.5rem;
        }

        .logo-badge {
          background: linear-gradient(135deg, var(--blue), var(--indigo));
          color: #fff;
          font-weight: 800;
          font-size: 1.2rem;
          width: 38px;
          height: 38px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 0 15px rgba(88, 166, 255, 0.4);
        }

        .logo-title {
          font-size: 1.25rem;
          font-weight: 700;
          background: linear-gradient(90deg, #fff, #8b949e);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .nav-menu {
          display: flex;
          flex-direction: column;
          gap: 6px;
          flex-grow: 1;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: 6px;
          color: var(--text-sec);
          text-decoration: none;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .nav-item:hover {
          background-color: rgba(48, 54, 61, 0.5);
          color: var(--text-main);
        }

        .nav-item.active {
          background-color: var(--blue);
          color: #fff;
          box-shadow: 0 4px 12px rgba(88, 166, 255, 0.25);
        }

        .sidebar-footer {
          border-top: 1px solid var(--border);
          padding-top: 1rem;
          font-size: 0.8rem;
          color: var(--text-sec);
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .pulse-light {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: var(--emerald);
          box-shadow: 0 0 8px var(--emerald);
          animation: pulse 2s infinite;
        }

        /* Main Workspace Content */
        .workspace {
          margin-left: 260px;
          flex-grow: 1;
          padding: 2rem;
          min-width: 0;
          box-sizing: border-box;
        }

        .header-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid var(--border);
          padding-bottom: 1.5rem;
          margin-bottom: 2rem;
        }

        .page-title {
          font-size: 1.75rem;
          font-weight: 700;
          margin: 0;
        }

        .page-subtitle {
          font-size: 0.9rem;
          color: var(--text-sec);
          margin-top: 4px;
        }

        /* Grid & Cards System */
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .stats-card {
          background-color: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          position: relative;
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .stats-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(0,0,0,0.3);
          border-color: #484f58;
        }

        .stats-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 4px;
          background: linear-gradient(90deg, transparent, var(--blue), transparent);
          opacity: 0;
          transition: opacity 0.3s;
        }

        .stats-card:hover::before {
          opacity: 1;
        }

        .stats-label {
          font-size: 0.85rem;
          color: var(--text-sec);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          font-weight: 600;
        }

        .stats-value {
          font-size: 2.25rem;
          font-weight: 700;
          color: #fff;
          margin: 0.5rem 0 0.25rem 0;
        }

        .stats-trend {
          font-size: 0.8rem;
          color: var(--emerald);
          display: flex;
          align-items: center;
          gap: 4px;
        }

        /* Custom Table Design */
        .card-container {
          background-color: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 1.5rem;
          margin-bottom: 2rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.25rem;
          flex-wrap: wrap;
          gap: 10px;
        }

        .card-title {
          font-size: 1.2rem;
          font-weight: 600;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .filters-group {
          display: flex;
          gap: 8px;
        }

        .select-filter {
          background-color: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: 6px;
          color: var(--text-main);
          padding: 6px 12px;
          font-size: 0.85rem;
          outline: none;
          cursor: pointer;
        }

        .select-filter:focus {
          border-color: var(--blue);
        }

        .datatable-wrapper {
          overflow-x: auto;
        }

        .datatable {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
          font-size: 0.9rem;
        }

        .datatable th {
          border-bottom: 2px solid var(--border);
          padding: 12px;
          color: var(--text-sec);
          font-weight: 600;
        }

        .datatable td {
          border-bottom: 1px solid var(--border);
          padding: 12px;
          vertical-align: middle;
        }

        .datatable tr:hover td {
          background-color: rgba(48, 54, 61, 0.25);
        }

        /* Status Badges */
        .badge {
          display: inline-flex;
          align-items: center;
          padding: 4px 8px;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .badge-verified { background-color: rgba(63, 185, 80, 0.15); color: var(--emerald); border: 1px solid rgba(63, 185, 80, 0.3); }
        .badge-unverified { background-color: rgba(210, 153, 34, 0.15); color: var(--amber); border: 1px solid rgba(210, 153, 34, 0.3); }
        
        .badge-pending { background-color: rgba(210, 153, 34, 0.15); color: var(--amber); }
        .badge-approved { background-color: rgba(88, 166, 255, 0.15); color: var(--blue); }
        .badge-completed { background-color: rgba(63, 185, 80, 0.15); color: var(--emerald); }
        .badge-cancelled { background-color: rgba(248, 81, 73, 0.15); color: var(--red); }

        .badge-role-barber { background-color: rgba(111, 66, 193, 0.15); color: #ab7df8; border: 1px solid rgba(111, 66, 193, 0.3); }
        .badge-role-salon { background-color: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid rgba(88, 166, 255, 0.3); }
        .badge-role-client { background-color: rgba(139, 148, 158, 0.15); color: var(--text-sec); border: 1px solid rgba(139, 148, 158, 0.3); }
        .badge-role-admin { background-color: rgba(248, 81, 73, 0.15); color: var(--red); border: 1px solid rgba(248, 81, 73, 0.3); }

        /* Actions buttons */
        .btn {
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          border: 1px solid transparent;
          transition: all 0.15s ease;
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }

        .btn-primary { background-color: var(--blue); color: #fff; }
        .btn-primary:hover { background-color: #1f6feb; }
        
        .btn-success { background-color: var(--emerald); color: #fff; }
        .btn-success:hover { background-color: #2ea44f; }

        .btn-secondary { background-color: var(--bg-card); color: var(--text-main); border-color: var(--border); }
        .btn-secondary:hover { background-color: var(--border); }

        .btn-danger { background-color: transparent; color: var(--red); border-color: rgba(248, 81, 73, 0.2); }
        .btn-danger:hover { background-color: var(--red); color: #fff; }

        .btn-disabled { opacity: 0.5; cursor: not-allowed; }

        /* Modal Dialog Styling (Glassmorphic Backdrop) */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s ease;
        }

        .modal-body {
          background-color: var(--bg-secondary);
          border: 1px solid var(--border);
          width: 550px;
          max-width: 90vw;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 10px 30px rgba(0,0,0,0.5);
          position: relative;
          animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .modal-title {
          font-size: 1.4rem;
          font-weight: 700;
          margin: 0;
        }

        .modal-close-btn {
          background: none;
          border: none;
          color: var(--text-sec);
          cursor: pointer;
          font-size: 1.5rem;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 4px;
          border-radius: 50%;
        }

        .modal-close-btn:hover {
          background-color: var(--border);
          color: #fff;
        }

        .modal-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.25rem;
          margin-bottom: 1.5rem;
        }

        .modal-field {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .modal-field-label {
          font-size: 0.8rem;
          color: var(--text-sec);
          font-weight: 600;
          text-transform: uppercase;
        }

        .modal-field-value {
          font-size: 0.95rem;
          color: var(--text-main);
        }

        .modal-field-full {
          grid-column: 1 / -1;
        }

        /* Toast Message Notification */
        .toast {
          position: fixed;
          bottom: 2rem;
          right: 2rem;
          padding: 12px 24px;
          border-radius: 8px;
          color: #fff;
          font-weight: 600;
          box-shadow: 0 8px 24px rgba(0,0,0,0.35);
          z-index: 10000;
          animation: slideLeft 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .toast-success { background-color: var(--emerald); border-left: 5px solid #2ea44f; }
        .toast-warning { background-color: var(--amber); border-left: 5px solid #b5841b; color: #000; }
        .toast-danger { background-color: var(--red); border-left: 5px solid #cf352e; }

        /* AI Scanning Simulation Visuals */
        .ai-scanning-overlay {
          background: linear-gradient(180deg, rgba(111, 66, 193, 0.1) 0%, rgba(88, 166, 255, 0.1) 100%);
          border: 2px dashed var(--indigo);
          border-radius: 8px;
          padding: 1.5rem;
          text-align: center;
          position: relative;
          overflow: hidden;
          margin-bottom: 1.5rem;
        }

        .ai-laser {
          position: absolute;
          width: 100%;
          height: 3px;
          background: linear-gradient(90deg, transparent, var(--blue), var(--indigo), var(--blue), transparent);
          top: 0;
          left: 0;
          animation: laserMove 2.5s infinite linear;
          box-shadow: 0 0 10px var(--blue);
        }

        /* Animations */
        @keyframes pulse {
          0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(63, 185, 80, 0.7); }
          70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(63, 185, 80, 0); }
          100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(63, 185, 80, 0); }
        }

        @keyframes laserMove {
          0% { top: 0%; }
          50% { top: 100%; }
          100% { top: 0%; }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        @keyframes slideLeft {
          from { transform: translateX(100px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }

        /* Responsive Breakpoints */
        @media (max-width: 900px) {
          .sidebar {
            width: 70px;
            padding: 1.5rem 0.5rem;
          }
          .logo-title, .sidebar-footer span, .nav-item span {
            display: none;
          }
          .logo-section {
            justify-content: center;
            padding: 0;
          }
          .workspace {
            margin-left: 70px;
            padding: 1.5rem;
          }
          .stats-grid {
            grid-template-columns: 1fr 1fr;
          }
        }

        @media (max-width: 600px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }
          .workspace {
            padding: 1rem;
          }
          .card-header {
            flex-direction: column;
            align-items: flex-start;
          }
          .filters-group {
            width: 100%;
          }
          .select-filter {
            flex-grow: 1;
          }
        }
      ` }} />

      {/* SIDEBAR NAVIGATION PANEL */}
      <aside className="sidebar">
        <div className="logo-section">
          <div className="logo-badge">IQ</div>
          <span className="logo-title">Hairlync Admin</span>
        </div>

        <nav className="nav-menu">
          <div className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>
            <span>Overview</span>
          </div>

          <div className={`nav-item ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
            <span>Users & Profiles</span>
          </div>

          <div className={`nav-item ${activeTab === 'bookings' ? 'active' : ''}`} onClick={() => setActiveTab('bookings')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
            <span>Bookings</span>
          </div>

          <div className={`nav-item ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => setActiveTab('ai')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 2 7 12 12 22 7 12 2" /><polyline points="2 17 12 22 22 17" /><polyline points="2 12 12 17 22 12" /></svg>
            <span>AI Recommendations</span>
          </div>

          <div className={`nav-item ${activeTab === 'reviews' ? 'active' : ''}`} onClick={() => setActiveTab('reviews')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
            <span>Review Moderation</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="pulse-light"></div>
          <span>API Services Online</span>
        </div>
      </aside>

      {/* WORKSPACE AREA */}
      <main className="workspace">
        {/* HEADER BAR */}
        <header className="header-bar">
          <div>
            <h1 className="page-title">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Dashboard</h1>
            <div className="page-subtitle">Real-time control over Hairlync models, user groups, and platform statistics.</div>
          </div>
          <div className="btn btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 4v6h-6" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" /></svg>
            <span>Refresh System</span>
          </div>
        </header>

        {/* ====================================================================
            TAB: OVERVIEW
            ==================================================================== */}
        {activeTab === 'overview' && (
          <div>
            {/* Stats Summary Cards */}
            <div className="stats-grid">
              <div className="stats-card">
                <span className="stats-label">MRR Recurring</span>
                <span className="stats-value">{stats.mrr}</span>
                <span className="stats-trend">↑ 8.4% from last week</span>
              </div>
              <div className="stats-card">
                <span className="stats-label">Registered Accounts</span>
                <span className="stats-value">{stats.totalUsers}</span>
                <span className="stats-trend" style={{ color: 'var(--text-sec)' }}>4 Providers Pending</span>
              </div>
              <div className="stats-card">
                <span className="stats-label">Active Bookings</span>
                <span className="stats-value">{bookings.filter(b => b.status === 'approved').length}</span>
                <span className="stats-trend" style={{ color: 'var(--amber)' }}>{stats.pendingBookings} Requires Approval</span>
              </div>
              <div className="stats-card">
                <span className="stats-label">AI Model Performance</span>
                <span className="stats-value">{stats.aiAccuracy}</span>
                <span className="stats-trend">Healthy (99.8% uptime)</span>
              </div>
            </div>

            {/* Main Graphs & Information Panels */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', flexWrap: 'wrap' }}>
              <div className="card-container">
                <h3 className="card-title">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>
                  System Latency & Analytics (Last 24 Hours)
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '1.5rem' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                      <span>AI Portrait Scanning Latency (Google Studio API)</span>
                      <strong style={{ color: 'var(--blue)' }}>124ms (Avg)</strong>
                    </div>
                    <div style={{ width: '100%', backgroundColor: 'var(--bg-primary)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: '35%', backgroundColor: 'var(--blue)', height: '100%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                      <span>DRF Database Read/Write Response Time</span>
                      <strong style={{ color: 'var(--emerald)' }}>42ms (Avg)</strong>
                    </div>
                    <div style={{ width: '100%', backgroundColor: 'var(--bg-primary)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: '15%', backgroundColor: 'var(--emerald)', height: '100%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                      <span>Image Storage Upload Speeds (AWS S3 Bucket)</span>
                      <strong style={{ color: 'var(--amber)' }}>286ms (Avg)</strong>
                    </div>
                    <div style={{ width: '100%', backgroundColor: 'var(--bg-primary)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: '65%', backgroundColor: 'var(--amber)', height: '100%' }}></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card-container">
                <h3 className="card-title">Quick Action Center</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '1.25rem' }}>
                  <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }} onClick={() => setActiveTab('reviews')}>
                    <span className="badge badge-cancelled" style={{ padding: '2px 6px', fontSize: '0.7rem' }}>{stats.flaggedReviews}</span>
                    <span>Moderate Flagged Reviews</span>
                  </button>
                  <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }} onClick={() => setActiveTab('users')}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" /></svg>
                    <span>Verify Pending Stylists</span>
                  </button>
                  <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'flex-start' }} onClick={() => setActiveTab('bookings')}>
                    <span className="badge badge-pending" style={{ padding: '2px 6px', fontSize: '0.7rem' }}>{stats.pendingBookings}</span>
                    <span>Review Pending Bookings</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ====================================================================
            TAB: USERS & PROFILES
            ==================================================================== */}
        {activeTab === 'users' && (
          <div className="card-container">
            <div className="card-header">
              <h3 className="card-title">Registered Accounts Database</h3>
              <div className="filters-group">
                <select className="select-filter" value={userRoleFilter} onChange={(e) => setUserRoleFilter(e.target.value)}>
                  <option value="all">All Roles</option>
                  <option value="barber">Barbers / Stylists</option>
                  <option value="salon">Salon Businesses</option>
                  <option value="client">Clients</option>
                  <option value="admin">Administrators</option>
                </select>
              </div>
            </div>

            <div className="datatable-wrapper">
              <table className="datatable">
                <thead>
                  <tr>
                    <th>Email Address</th>
                    <th>Full Name</th>
                    <th>Role</th>
                    <th>Sub-Account?</th>
                    <th>Verification</th>
                    <th>Status</th>
                    <th>Joined</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users
                    .filter(u => userRoleFilter === 'all' || u.role === userRoleFilter)
                    .map(user => (
                      <tr key={user.id}>
                        <td style={{ fontWeight: '500' }}>{user.email}</td>
                        <td>{user.full_name || 'N/A'}</td>
                        <td>
                          <span className={`badge badge-role-${user.role}`}>
                            {user.role.toUpperCase()}
                          </span>
                        </td>
                        <td>{user.is_sub_profile ? 'Yes (Employee)' : 'No (Owner)'}</td>
                        <td>
                          <span className={`badge ${user.is_verified ? 'badge-verified' : 'badge-unverified'}`}>
                            {user.is_verified ? 'Verified' : 'Pending'}
                          </span>
                        </td>
                        <td>
                          <span style={{ color: user.is_active ? 'var(--emerald)' : 'var(--red)', fontWeight: '600' }}>
                            {user.is_active ? 'Active' : 'Suspended'}
                          </span>
                        </td>
                        <td style={{ color: 'var(--text-sec)', fontSize: '0.85rem' }}>{user.date_joined}</td>
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', gap: '6px' }}>
                            <button className="btn btn-secondary" style={{ padding: '4px 8px' }} onClick={() => setSelectedUser(user)}>
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></svg>
                            </button>
                            {user.role !== 'client' && user.role !== 'admin' && (
                              <button className="btn btn-primary" style={{ padding: '4px 8px', backgroundColor: user.is_verified ? 'var(--amber)' : 'var(--emerald)' }} onClick={() => handleToggleVerifyUser(user.id)}>
                                {user.is_verified ? 'Revoke' : 'Verify'}
                              </button>
                            )}
                            <button className="btn btn-danger" style={{ padding: '4px 8px' }} onClick={() => handleDeleteUser(user.id)}>
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /><line x1="10" y1="11" x2="10" y2="17" /><line x1="14" y1="11" x2="14" y2="17" /></svg>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ====================================================================
            TAB: BOOKINGS
            ==================================================================== */}
        {activeTab === 'bookings' && (
          <div className="card-container">
            <div className="card-header">
              <h3 className="card-title">Manage Customer Appointments</h3>
              <div className="filters-group">
                <select className="select-filter" value={bookingStatusFilter} onChange={(e) => setBookingStatusFilter(e.target.value)}>
                  <option value="all">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </div>

            <div className="datatable-wrapper">
              <table className="datatable">
                <thead>
                  <tr>
                    <th>Booking ID</th>
                    <th>Client</th>
                    <th>Barber Studio / Stylist</th>
                    <th>Service Requested</th>
                    <th>Date & Time</th>
                    <th>Price</th>
                    <th>Status</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings
                    .filter(b => bookingStatusFilter === 'all' || b.status === bookingStatusFilter)
                    .map(b => (
                      <tr key={b.id}>
                        <td style={{ fontWeight: '600' }}>#{b.id}</td>
                        <td>{b.client}</td>
                        <td>{b.provider}</td>
                        <td>{b.service}</td>
                        <td>{b.date} • {b.time}</td>
                        <td style={{ fontWeight: '600', color: 'var(--emerald)' }}>{b.price}</td>
                        <td>
                          <span className={`badge badge-${b.status}`}>
                            {b.status.toUpperCase()}
                          </span>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', gap: '6px' }}>
                            <button className="btn btn-secondary" style={{ padding: '4px 8px' }} onClick={() => setSelectedBooking(b)}>
                              Details
                            </button>
                            {b.status === 'pending' && (
                              <>
                                <button className="btn btn-success" style={{ padding: '4px 8px' }} onClick={() => handleBookingStatus(b.id, 'approved')}>
                                  Approve
                                </button>
                                <button className="btn btn-danger" style={{ padding: '4px 8px' }} onClick={() => handleBookingStatus(b.id, 'rejected')}>
                                  Reject
                                </button>
                              </>
                            )}
                            {b.status === 'approved' && (
                              <button className="btn btn-danger" style={{ padding: '4px 8px' }} onClick={() => handleBookingStatus(b.id, 'cancelled')}>
                                Cancel
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ====================================================================
            TAB: AI RECOMMENDATIONS
            ==================================================================== */}
        {activeTab === 'ai' && (
          <div className="card-container">
            <h3 className="card-title">AI Style recommendations Engine</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-sec)', marginBottom: '1.5rem' }}>
              Process uploaded customer portraits through the AI Model pipeline and output smart styling suggestions.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {aiItems.map(item => (
                <div key={item.id} style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '1.25rem', position: 'relative' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 'bold' }}>Request #{item.id}</span>
                    <span className={`badge ${item.status === 'completed' ? 'badge-completed' : 'badge-pending'}`}>
                      {item.status.toUpperCase()}
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '12px', marginBottom: '1rem' }}>
                    <div style={{ width: '80px', height: '80px', backgroundColor: 'var(--bg-primary)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyItems: 'center', justifyContent: 'center' }}>
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--text-sec)" strokeWidth="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 'bold' }}>{item.client}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-sec)' }}>Assigned Barber: {item.provider}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-sec)', marginTop: '4px' }}>Hair Length: <span style={{ textTransform: 'capitalize', color: 'var(--blue)', fontWeight: '600' }}>{item.hair_length}</span></div>
                    </div>
                  </div>

                  <div style={{ fontSize: '0.85rem', color: 'var(--text-sec)', backgroundColor: 'var(--bg-primary)', padding: '8px', borderRadius: '4px', marginBottom: '1rem' }}>
                    <strong>Client Notes:</strong> {item.notes}
                  </div>

                  {item.status === 'completed' && (
                    <div style={{ fontSize: '0.85rem', borderLeft: '3px solid var(--indigo)', paddingLeft: '8px', marginBottom: '1.25rem' }}>
                      <strong>AI Suggestion:</strong> <span style={{ color: '#ab7df8', fontWeight: 'bold' }}>{item.recommended_style}</span>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-secondary" style={{ flexGrow: 1 }} onClick={() => setSelectedAi(item)}>
                      View File
                    </button>
                    {item.status === 'pending' && (
                      <button className={`btn btn-primary ${analyzingId === item.id ? 'btn-disabled' : ''}`} style={{ flexGrow: 1 }} disabled={analyzingId === item.id} onClick={() => handleRunAIRecommendation(item.id)}>
                        {analyzingId === item.id ? 'Analyzing...' : 'Run AI Analysis'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ====================================================================
            TAB: REVIEWS
            ==================================================================== */}
        {activeTab === 'reviews' && (
          <div className="card-container">
            <div className="card-header">
              <h3 className="card-title">Customer Feedback Moderation</h3>
              <div className="filters-group">
                <select className="select-filter" value={reviewFilter} onChange={(e) => setReviewFilter(e.target.value)}>
                  <option value="all">All Reviews</option>
                  <option value="flagged">Flagged / Reported Only</option>
                  <option value="approved">Approved</option>
                </select>
              </div>
            </div>

            <div className="datatable-wrapper">
              <table className="datatable">
                <thead>
                  <tr>
                    <th>Client</th>
                    <th>Barber Studio</th>
                    <th>Rating</th>
                    <th>Comment</th>
                    <th>Moderation</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reviews
                    .filter(r => {
                      if (reviewFilter === 'flagged') return r.is_flagged;
                      if (reviewFilter === 'approved') return r.is_approved;
                      return true;
                    })
                    .map(r => (
                      <tr key={r.id}>
                        <td style={{ fontWeight: '500' }}>{r.client}</td>
                        <td>{r.provider}</td>
                        <td style={{ color: 'var(--amber)', fontWeight: 'bold' }}>
                          {'★'.repeat(r.rating) + '☆'.repeat(5 - r.rating)}
                        </td>
                        <td style={{ maxWidth: '280px', fontSize: '0.85rem' }}>"{r.comment}"</td>
                        <td>
                          {r.is_flagged ? (
                            <span className="badge badge-cancelled" style={{ gap: '4px' }}>
                              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
                              FLAGGED
                            </span>
                          ) : (
                            <span className="badge badge-verified">APPROVED</span>
                          )}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', gap: '6px' }}>
                            {r.is_flagged ? (
                              <button className="btn btn-success" style={{ padding: '4px 8px' }} onClick={() => handleReviewAction(r.id, 'approve')}>
                                Approve Review
                              </button>
                            ) : (
                              <button className="btn btn-secondary" style={{ padding: '4px 8px' }} onClick={() => handleReviewAction(r.id, 'flag')}>
                                Flag Content
                              </button>
                            )}
                            <button className="btn btn-danger" style={{ padding: '4px 8px' }} onClick={() => handleReviewAction(r.id, 'delete')}>
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* ====================================================================
          MODAL: USER DETAILS
          ==================================================================== */}
      {selectedUser && (
        <div className="modal-overlay" onClick={() => setSelectedUser(null)}>
          <div className="modal-body" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h4 className="modal-title">User Account Overview</h4>
              <button className="modal-close-btn" onClick={() => setSelectedUser(null)}>&times;</button>
            </div>

            <div className="modal-grid">
              <div className="modal-field">
                <span className="modal-field-label">Full Name</span>
                <span className="modal-field-value">{selectedUser.full_name || 'N/A'}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Email Address</span>
                <span className="modal-field-value">{selectedUser.email}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">User Role</span>
                <span className="modal-field-value">
                  <span className={`badge badge-role-${selectedUser.role}`}>{selectedUser.role.toUpperCase()}</span>
                </span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Subscription tier</span>
                <span className="modal-field-value" style={{ textTransform: 'capitalize' }}>{selectedUser.plan}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Verification Status</span>
                <span className="modal-field-value">{selectedUser.is_verified ? 'Verified Partner' : 'Unverified Partner'}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Date Joined</span>
                <span className="modal-field-value">{selectedUser.date_joined}</span>
              </div>
              {selectedUser.role !== 'client' && (
                <>
                  <div className="modal-field">
                    <span className="modal-field-label">Business Studio Name</span>
                    <span className="modal-field-value">{selectedUser.business_name || 'Individual Barber'}</span>
                  </div>
                  <div className="modal-field">
                    <span className="modal-field-label">Average Reviews Score</span>
                    <span className="modal-field-value" style={{ color: 'var(--amber)', fontWeight: 'bold' }}>{selectedUser.rating} ★ ({selectedUser.total_bookings} Bookings)</span>
                  </div>
                </>
              )}
            </div>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', borderTop: '1px solid var(--border)', paddingTop: '1.25rem' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedUser(null)}>Close</button>
              {selectedUser.role !== 'client' && (
                <button className="btn btn-primary" style={{ backgroundColor: selectedUser.is_verified ? 'var(--amber)' : 'var(--emerald)' }} onClick={() => handleToggleVerifyUser(selectedUser.id)}>
                  {selectedUser.is_verified ? 'Unverify Account' : 'Verify Account'}
                </button>
              )}
              <button className="btn btn-secondary" style={{ backgroundColor: selectedUser.is_active ? 'rgba(248, 81, 73, 0.15)' : 'rgba(63, 185, 80, 0.15)', color: selectedUser.is_active ? 'var(--red)' : 'var(--emerald)' }} onClick={() => handleToggleActiveUser(selectedUser.id)}>
                {selectedUser.is_active ? 'Suspend Account' : 'Activate Account'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ====================================================================
          MODAL: BOOKING DETAILS
          ==================================================================== */}
      {selectedBooking && (
        <div className="modal-overlay" onClick={() => setSelectedBooking(null)}>
          <div className="modal-body" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h4 className="modal-title">Booking Appointment #{selectedBooking.id}</h4>
              <button className="modal-close-btn" onClick={() => setSelectedBooking(null)}>&times;</button>
            </div>

            <div className="modal-grid">
              <div className="modal-field">
                <span className="modal-field-label">Client Name</span>
                <span className="modal-field-value">{selectedBooking.client}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Stylist / Partner</span>
                <span className="modal-field-value">{selectedBooking.provider}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Service Description</span>
                <span className="modal-field-value">{selectedBooking.service}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Price Rate</span>
                <span className="modal-field-value" style={{ color: 'var(--emerald)', fontWeight: 'bold' }}>{selectedBooking.price}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Appointment Time</span>
                <span className="modal-field-value">{selectedBooking.date} at {selectedBooking.time}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Schedule Status</span>
                <span className="modal-field-value">
                  <span className={`badge badge-${selectedBooking.status}`}>{selectedBooking.status.toUpperCase()}</span>
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', borderTop: '1px solid var(--border)', paddingTop: '1.25rem' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedBooking(null)}>Close</button>
              {selectedBooking.status === 'pending' && (
                <>
                  <button className="btn btn-success" onClick={() => handleBookingStatus(selectedBooking.id, 'approved')}>Approve</button>
                  <button className="btn btn-danger" onClick={() => handleBookingStatus(selectedBooking.id, 'rejected')}>Reject</button>
                </>
              )}
              {selectedBooking.status === 'approved' && (
                <button className="btn btn-danger" onClick={() => handleBookingStatus(selectedBooking.id, 'cancelled')}>Cancel Booking</button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ====================================================================
          MODAL: AI RECOMMENDATION DRAWER
          ==================================================================== */}
      {selectedAi && (
        <div className="modal-overlay" onClick={() => setSelectedAi(null)}>
          <div className="modal-body" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h4 className="modal-title">AI Recommendation Report</h4>
              <button className="modal-close-btn" onClick={() => setSelectedAi(null)}>&times;</button>
            </div>

            {analyzingId === selectedAi.id ? (
              <div className="ai-scanning-overlay">
                <div className="ai-laser"></div>
                <div style={{ color: '#ab7df8', fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '8px' }}>Hairlync AI Model Running...</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-sec)' }}>Analyzing hair follicle density, length structures, and facial features.</div>
              </div>
            ) : selectedAi.status === 'pending' ? (
              <div className="ai-scanning-overlay" style={{ borderStyle: 'solid', borderColor: 'var(--border)', background: 'none' }}>
                <div style={{ fontWeight: 'bold', fontSize: '1rem', color: 'var(--amber)', marginBottom: '8px' }}>Analysis Status: Pending</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-sec)' }}>This portrait image is queued and ready for AI model processing.</div>
              </div>
            ) : (
              <div className="ai-scanning-overlay" style={{ borderStyle: 'solid', borderColor: 'var(--emerald)', backgroundColor: 'rgba(63, 185, 80, 0.05)' }}>
                <div style={{ color: 'var(--emerald)', fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '8px' }}>Analysis Successful</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-sec)' }}>Style output generated using Google Studio AI module.</div>
              </div>
            )}

            <div className="modal-grid">
              <div className="modal-field">
                <span className="modal-field-label">Customer Client</span>
                <span className="modal-field-value">{selectedAi.client}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Barber Studio</span>
                <span className="modal-field-value">{selectedAi.provider}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Follicle Hair Length</span>
                <span className="modal-field-value" style={{ textTransform: 'capitalize' }}>{selectedAi.hair_length}</span>
              </div>
              <div className="modal-field">
                <span className="modal-field-label">Request Date</span>
                <span className="modal-field-value">{selectedAi.date}</span>
              </div>
              <div className="modal-field modal-field-full">
                <span className="modal-field-label">Client Notes</span>
                <span className="modal-field-value" style={{ fontStyle: 'italic' }}>"{selectedAi.notes}"</span>
              </div>
              {selectedAi.status === 'completed' && (
                <div className="modal-field modal-field-full" style={{ backgroundColor: 'var(--bg-primary)', padding: '12px', borderRadius: '6px' }}>
                  <span className="modal-field-label" style={{ color: '#ab7df8' }}>AI Recommended Hair Style</span>
                  <span className="modal-field-value" style={{ fontSize: '1.15rem', fontWeight: 'bold', color: '#fff', marginTop: '4px' }}>{selectedAi.recommended_style}</span>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', borderTop: '1px solid var(--border)', paddingTop: '1.25rem' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedAi(null)}>Close</button>
              {selectedAi.status === 'pending' && (
                <button className={`btn btn-primary ${analyzingId === selectedAi.id ? 'btn-disabled' : ''}`} disabled={analyzingId === selectedAi.id} onClick={() => handleRunAIRecommendation(selectedAi.id)}>
                  {analyzingId === selectedAi.id ? 'Running AI Engine...' : 'Run AI Analysis'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* GLOBAL TOAST NOTIFICATION CONTAINER */}
      {toast.show && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' && <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg>}
          {toast.type === 'warning' && <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>}
          {toast.type === 'danger' && <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>}
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
}
