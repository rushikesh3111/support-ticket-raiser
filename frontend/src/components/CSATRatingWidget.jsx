import React, { useState } from 'react';
import { apiRequest } from '../services/api';
import confetti from 'canvas-confetti';
import { Star, MessageCircle, CheckCircle2, X } from 'lucide-react';

export default function CSATRatingWidget({ ticketId, onSubmitted }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating === 0) return;
    setLoading(true);
    try {
      await apiRequest(`/actions/tickets/${ticketId}/csat`, {
        method: 'POST',
        body: JSON.stringify({ score: rating, feedback })
      });
      setSubmitted(true);
      // Trigger festive celebration confetti
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
      if (onSubmitted) onSubmitted();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-center animate-in zoom-in-95">
        <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-1.5" />
        <h4 className="text-xs font-bold text-emerald-900">Thank You for Your Feedback!</h4>
        <p className="text-[11px] text-emerald-700 mt-0.5">Your rating helps us improve support quality.</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50/50 border border-amber-200/70 rounded-2xl space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-amber-900 uppercase tracking-wider">Rate Resolution Quality</span>
        <span className="text-[10px] bg-amber-200/80 text-amber-800 font-bold px-2 py-0.5 rounded-full">CSAT</span>
      </div>

      <div className="flex items-center justify-center gap-2 py-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => setRating(star)}
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            className="p-1 text-slate-300 hover:scale-125 transition-transform"
          >
            <Star
              className={`w-6 h-6 transition-colors ${
                (hoverRating || rating) >= star
                  ? 'text-amber-500 fill-amber-400'
                  : 'text-slate-300'
              }`}
            />
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="text"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Optional feedback: How was the agent's assistance?"
          className="w-full px-3 py-1.5 text-xs bg-white border border-amber-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 font-medium placeholder:text-slate-400"
        />
        <button
          type="submit"
          disabled={loading || rating === 0}
          className="w-full py-2 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-sm transition"
        >
          {loading ? 'Submitting...' : 'Submit Rating'}
        </button>
      </form>
    </div>
  );
}
