// app/violations/page.jsx
'use client';

import { useEffect, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Filter,
  Loader2
} from 'lucide-react';
import { api } from '../../../lib/api';

export default function Violations() {
  const [violations, setViolations] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState({});

  useEffect(() => {
    fetchViolations();
  }, []);

  const fetchViolations = async () => {
    try {
      const response = await api.get('/dashboard/violations?limit=50');
      setViolations(response.data || []);
    } catch (error) {
      console.error('Error fetching violations:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveViolation = async (id) => {
    setResolving(prev => ({ ...prev, [id]: true }));
    try {
      await api.put(`/dashboard/resolve/${id}`);
      await fetchViolations();
    } catch (error) {
      console.error('Error resolving violation:', error);
    } finally {
      setResolving(prev => ({ ...prev, [id]: false }));
    }
  };

  const getSeverityStyle = (severity = '') => {
    const level = severity.toLowerCase();
    if (level === 'high')
      return 'bg-red-100 text-red-700 border-red-200';
    if (level === 'medium')
      return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    if (level === 'low')
      return 'bg-blue-100 text-blue-700 border-blue-200';
    return 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const getStatusBadge = (status = '') => {
    const s = status.toLowerCase();
    if (s === 'open')
      return (
        <span className="flex items-center gap-1 text-red-600 text-sm font-medium">
          <XCircle size={16} />
          Open
        </span>
      );
    return (
      <span className="flex items-center gap-1 text-green-600 text-sm font-medium">
        <CheckCircle2 size={16} />
        Resolved
      </span>
    );
  };

  const filteredViolations = violations.filter(v => {
    if (filter === 'all') return true;
    return v.status?.toLowerCase() === filter;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-72">
        <Loader2 className="animate-spin text-blue-600" size={30} />
      </div>
    );
  }

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <h1 className="text-2xl font-bold text-gray-800">
          Compliance Violations
        </h1>

        <div className="flex items-center gap-3">
          <Filter size={18} className="text-gray-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 border rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            <option value="open">Open</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Empty State */}
      {filteredViolations.length === 0 ? (
        <div className="bg-white border rounded-xl shadow-sm p-12 text-center">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500 text-lg font-medium">
            No Violations Found
          </p>
          <p className="text-sm text-gray-400 mt-2">
            Your system is currently compliant 🎉
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredViolations.map((violation) => (
            <div
              key={violation.id}
              className="bg-white border rounded-xl shadow-sm p-5 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">

                <div className="space-y-2 flex-1">

                  {/* Top Row */}
                  <div className="flex items-center gap-4 flex-wrap">
                    {getStatusBadge(violation.status)}

                    <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${getSeverityStyle(violation.severity)}`}>
                      {violation.severity}
                    </span>

                    <span className="text-gray-600 text-sm">
                      Table: <span className="font-medium">{violation.table_name}</span>
                    </span>

                    <span className="text-gray-400 text-sm">
                      Record ID: {violation.record_id}
                    </span>
                  </div>

                  {/* Message */}
                  <p className="text-gray-700">
                    {violation.message}
                  </p>

                  {/* Remediation */}
                  {violation.remediation && (
                    <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
                      <p className="text-sm font-medium text-blue-800">
                        Recommended Action
                      </p>
                      <p className="text-sm text-blue-600 mt-1">
                        {violation.remediation}
                      </p>
                    </div>
                  )}

                  {/* Timestamp */}
                  <p className="text-xs text-gray-400 pt-2">
                    Detected on {new Date(violation.created_at).toLocaleString()}
                  </p>
                </div>

                {/* Resolve Button */}
                {violation.status?.toLowerCase() === 'open' && (
                  <button
                    onClick={() => resolveViolation(violation.id)}
                    disabled={resolving[violation.id]}
                    className="ml-4 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:bg-gray-400 transition"
                  >
                    {resolving[violation.id] ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      'Resolve'
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}