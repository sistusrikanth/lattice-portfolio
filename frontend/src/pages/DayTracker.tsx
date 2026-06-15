import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { todayISO, usePrivateToken } from "../lib/auth";
import PrivateShell from "../components/PrivateShell";
import type { DayEntry } from "../lib/types";
import "./PrivatePages.css";

function formatEntryDate(iso: string): string {
  const d = new Date(iso + "T12:00:00");
  return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
}

export default function DayTrackerPage() {
  const token = usePrivateToken();
  const today = todayISO();
  const [selectedDate, setSelectedDate] = useState(today);
  const [personal, setPersonal] = useState("");
  const [professional, setProfessional] = useState("");
  const [entries, setEntries] = useState<DayEntry[]>([]);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadEntries = async () => {
    const list = await api.getDayEntries(token);
    setEntries(list);
  };

  const loadDay = async (date: string) => {
    setLoading(true);
    setSaved(false);
    try {
      const entry = await api.getDayEntry(token, date);
      setPersonal(entry.personal);
      setProfessional(entry.professional);
    } catch {
      setPersonal("");
      setProfessional("");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEntries().catch(() => {});
  }, [token]);

  useEffect(() => {
    loadDay(selectedDate);
  }, [selectedDate, token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.saveDayEntry(token, selectedDate, { personal, professional });
    setSaved(true);
    await loadEntries();
    setTimeout(() => setSaved(false), 2000);
  };

  const isToday = selectedDate === today;

  return (
    <PrivateShell>
      <p className="section-label"><span>§</span> Private Day tracker</p>
      <h1 className="page-title serif">{isToday ? "Today." : formatEntryDate(selectedDate)}</h1>
      <p className="page-subtitle">
        What you accomplished — personal and professional. One honest record per day.
      </p>

      <div className="day-date-row mono">
        <label>
          Date
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            max={today}
          />
        </label>
        {!isToday && (
          <button type="button" className="btn btn-outline" onClick={() => setSelectedDate(today)}>
            Jump to today
          </button>
        )}
      </div>

      {loading ? (
        <p className="mono private-muted">Loading…</p>
      ) : (
        <form className="day-form card" onSubmit={handleSave}>
          <label>
            <span className="day-label mono">Personal</span>
            <span className="day-hint">Health, relationships, rest, hobbies, life outside work</span>
            <textarea
              value={personal}
              onChange={(e) => setPersonal(e.target.value)}
              rows={5}
              placeholder="Morning run along the river. Called mom. Read for an hour before bed."
            />
          </label>
          <label>
            <span className="day-label mono">Professional</span>
            <span className="day-hint">Work shipped, learned, decided, or unblocked</span>
            <textarea
              value={professional}
              onChange={(e) => setProfessional(e.target.value)}
              rows={5}
              placeholder="Drafted the KV-cache piece. Reviewed a design doc. Fixed the deploy pipeline."
            />
          </label>
          <div className="day-form-actions">
            <button type="submit" className="btn btn-primary">
              {saved ? "Saved ✓" : "Save entry"}
            </button>
          </div>
        </form>
      )}

      <section className="day-history">
        <h2 className="mono day-history-title">Recent days</h2>
        {entries.length === 0 ? (
          <p className="mono private-muted">No entries yet. Start with today.</p>
        ) : (
          <div className="day-history-list">
            {entries.map((entry) => (
              <button
                key={entry.id}
                type="button"
                className={`day-history-item card ${entry.entry_date === selectedDate ? "active" : ""}`}
                onClick={() => setSelectedDate(entry.entry_date)}
              >
                <span className="mono day-history-date">{formatEntryDate(entry.entry_date)}</span>
                <div className="day-history-preview">
                  {entry.personal && (
                    <p><span className="mono">personal</span> {entry.personal.slice(0, 80)}{entry.personal.length > 80 ? "…" : ""}</p>
                  )}
                  {entry.professional && (
                    <p><span className="mono">work</span> {entry.professional.slice(0, 80)}{entry.professional.length > 80 ? "…" : ""}</p>
                  )}
                  {!entry.personal && !entry.professional && (
                    <p className="private-muted">Empty entry</p>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      <p className="private-footer-link">
        <Link to="/private/identity" className="mono">Who I am →</Link>
      </p>
    </PrivateShell>
  );
}
