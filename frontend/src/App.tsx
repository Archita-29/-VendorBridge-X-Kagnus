import { useEffect, useState } from "react";
import { api, type Vendor } from "./api";
import "./index.css";


type AuthUser = {
  id: number;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
};

function LoginScreen({ onLogin }: {
  onLogin: (user: AuthUser) => void;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.login(email.trim(), password);
      const user = await api.me() as AuthUser;
      onLogin(user);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed. Please check your details."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="brand-icon">V</div>
        <p className="eyebrow">VENDORBRIDGE ERP</p>
        <h1>Welcome back</h1>
        <p className="subtitle">Sign in to your procurement workspace.</p>

        {error && <div className="error-banner" role="alert">{error}</div>}

        <label htmlFor="login-email">Email address</label>
        <input
          id="login-email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="login-password">Password</label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}

function App() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    api.me()
      .then((data) => setUser(data as AuthUser))
      .catch(() => setUser(null))
      .finally(() => setAuthLoading(false));
  }, []);

  async function handleLogout() {
    try {
      await api.logout();
    } finally {
      setUser(null);
    }
  }
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [contactName, setContactName] = useState("");
  const [contact, setContact] = useState("");
  const [phone, setPhone] = useState("");

  async function loadVendors() {
    setLoading(true);
    setError("");
    try {
      const data = await api.listVendors();
      setVendors(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load vendors");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadVendors();
  }, []);

  const filteredVendors = vendors.filter((vendor) => {
    const text = `${vendor.vendor_name} ${vendor.category} ${vendor.contact_name} ${vendor.contact_email}`.toLowerCase();
    return text.includes(search.toLowerCase()) &&
      (filter === "All" || vendor.status.toLowerCase() === filter.toLowerCase());
  });

  async function addVendor(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await api.createVendor({
        vendor_name: name.trim(),
        category: category.trim(),
        contact_name: contactName.trim(),
        contact_email: contact.trim(),
        contact_phone: phone.trim(),
      });

      setName("");
      setCategory("");
      setContactName("");
      setContact("");
      setPhone("");
      setShowForm(false);
      await loadVendors();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create vendor");
    } finally {
      setSaving(false);
    }
  }
const stats = [
  {
    label: "Active RFQs",
    value: "—",
    icon: "↗",
    color: "blue",
    note: "RFQ module not implemented",
  },
  {
    label: "Pending Approvals",
    value: "—",
    icon: "◷",
    color: "amber",
    note: "Approval module not implemented",
  },
  {
    label: "Purchase Order Value",
    value: "—",
    icon: "₹",
    color: "green",
    note: "No purchase order data yet",
  },
  {
    label: "Active Vendors",
    value: vendors.filter(
      (vendor) => vendor.status.toLowerCase() === "approved"
    ).length.toString(),
    icon: "✓",
    color: "green",
    note: "Based on approved vendor records",
  },
];


    if (authLoading) {
    return <main className="auth-page">Checking your session...</main>;
  }

  if (!user) {
    return <LoginScreen onLogin={setUser} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">V</div>
          <div><h2>VendorBridge</h2><span>PROCUREMENT ERP</span></div>
        </div>
        <p className="nav-heading">WORKSPACE</p>
        <nav>
          <a className="nav-item active" href="#dashboard"><span>▦</span> Dashboard</a>
          <a className="nav-item" href="#vendors"><span>♙</span> Vendors <span className="nav-count">{vendors.length}</span></a>
          <a className="nav-item" href="#purchase-orders"><span>▤</span> Purchase Orders</a>
          <a className="nav-item" href="#invoices"><span>▧</span> Invoices</a>
          <a className="nav-item" href="#reports"><span>▥</span> Reports</a>
        </nav>
        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">?</div><strong>Need help?</strong>
            <p>Contact your procurement administrator.</p>
          </div>
          <div className="profile">
            <div className="avatar">V</div>
            <div className="profile-info"><strong>VendorBridge</strong><span>Development preview</span></div>
          </div>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> <strong>Dashboard</strong></div>
          <div className="topbar-right"><span className="environment">● Development</span><span>{user.full_name} · {user.role}</span><button className="secondary-button" onClick={() => void handleLogout()}>Log out</button></div>
        </header>

        <section className="page-content">
          <div className="welcome-row">
            <div><p className="eyebrow">OVERVIEW</p><h1>Procurement Dashboard</h1><p className="subtitle">Here's what's happening across your procurement workspace.</p></div>
            <button className="primary-button" onClick={() => setShowForm(true)}><span>＋</span> Add Vendor</button>
          </div>

          {error && <div className="error-banner" role="alert">{error}</div>}

          <div className="stats-grid">
            {stats.map((stat) => (
              <article className="stat-card" key={stat.label}>
                <div className={`stat-icon ${stat.color}`}>{stat.icon}</div>
                <p>{stat.label}</p>
                <div className="stat-bottom"><strong>{loading && stat.label === "Active Vendors" ? "—" : stat.value}</strong><span className="stat-note">{stat.note}</span></div>

              </article>
            ))}
          </div>

          <section className="content-card" id="vendors">
            <div className="card-heading">
              <div><h2>Vendor Directory</h2><p>Manage and review registered vendors.</p></div>
              <button className="secondary-button" onClick={() => setShowForm(true)}>＋ New Vendor</button>
            </div>
            <div className="table-toolbar">
              <div className="search-box"><span>⌕</span><input aria-label="Search vendors" placeholder="Search vendors, categories, contacts..." value={search} onChange={(e) => setSearch(e.target.value)} /></div>
              <select aria-label="Filter by status" value={filter} onChange={(e) => setFilter(e.target.value)}>
                <option>All</option><option>Approved</option><option>Pending</option><option>Rejected</option>
              </select>
              <button className="secondary-button" onClick={() => void loadVendors()}>Refresh</button>
            </div>
            <div className="table-scroll">
              <table>
                <thead><tr><th>VENDOR</th><th>CATEGORY</th><th>CONTACT EMAIL</th><th>STATUS</th></tr></thead>
                <tbody>
                  {loading ? <tr><td colSpan={4} className="empty-state">Loading vendors…</td></tr> :
                    filteredVendors.map((vendor) => (
                      <tr key={vendor.id}>
                        <td><div className="vendor-cell"><div className="vendor-avatar">{vendor.vendor_name.charAt(0)}</div><strong>{vendor.vendor_name}</strong></div></td>
                        <td>{vendor.category}</td><td className="contact-email">{vendor.contact_email}</td>
                        <td><span className={`status-badge ${vendor.status.toLowerCase()}`}>{vendor.status}</span></td>
                      </tr>
                    ))}
                  {!loading && filteredVendors.length === 0 && <tr><td colSpan={4} className="empty-state">No vendors found. Try another search or add a vendor.</td></tr>}
                </tbody>
              </table>
            </div>
            <div className="table-footer"><span>Showing <strong>{filteredVendors.length}</strong> of <strong>{vendors.length}</strong> vendors</span><span className="footer-label">Live API data</span></div>
          </section>
          <div className="bottom-note">ⓘ Purchase orders and invoices are future modules; no records are shown yet.</div>
        </section>

<div className="dashboard-lower-grid">
  <section className="content-card lower-card">
    <div className="card-heading">
      <div>
        <h2>Quick Actions</h2>
        <p>Common procurement tasks</p>
      </div>
    </div>

    <div className="quick-actions">
      <button onClick={() => setShowForm(true)}>
        <span className="quick-icon">＋</span>
        <span><strong>Add Vendor</strong><small>Register a new supplier</small></span>
        <span className="quick-arrow">↗</span>
      </button>

      <div className="quick-action-disabled">
        <span className="quick-icon">↗</span>
        <span><strong>Create RFQ</strong><small>RFQ module coming soon</small></span>
      </div>

      <div className="quick-action-disabled">
        <span className="quick-icon">▤</span>
        <span><strong>Create Purchase Order</strong><small>Order module coming soon</small></span>
      </div>
    </div>
  </section>

  <section className="content-card lower-card">
    <div className="card-heading">
      <div>
        <h2>Recent Activity</h2>
        <p>Latest recorded procurement activity</p>
      </div>
    </div>

    <div className="activity-empty">
      <span className="activity-empty-icon">◷</span>
      <strong>No activity recorded yet</strong>
      <p>Vendor and procurement activity will appear here when activity tracking is implemented.</p>
    </div>
  </section>
</div>

      </main>

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onClick={(e) => e.stopPropagation()}>
            <div className="modal-heading"><div><p className="eyebrow">VENDOR MANAGEMENT</p><h2 id="modal-title">Add a vendor</h2></div><button className="close-button" onClick={() => setShowForm(false)} aria-label="Close">×</button></div>
            <form onSubmit={addVendor}>
              <label>Vendor name<input required minLength={2} value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Apex Technologies" /></label>
              <label>Category<input required value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. IT Services" /></label>
              <label>Contact name<input required value={contactName} onChange={(e) => setContactName(e.target.value)} placeholder="Contact person" /></label>
              <label>Contact email<input required type="email" value={contact} onChange={(e) => setContact(e.target.value)} placeholder="vendor@example.com" /></label>
              <label>Contact phone<input required value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Phone number" /></label>
              <p className="form-note">New vendors start with Pending status.</p>
              <div className="modal-actions"><button type="button" className="secondary-button" onClick={() => setShowForm(false)}>Cancel</button><button disabled={saving} type="submit" className="primary-button">{saving ? "Saving…" : "Save Vendor"}</button></div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;