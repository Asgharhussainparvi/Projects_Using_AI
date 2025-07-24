import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [moods, setMoods] = useState([]);
  const [moodOptions, setMoodOptions] = useState({});
  const [selectedMood, setSelectedMood] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("entry"); // "entry", "history", "calendar"

  useEffect(() => {
    fetchMoodOptions();
    fetchMoods();
  }, []);

  const fetchMoodOptions = async () => {
    try {
      const response = await axios.get(`${API}/moods/options`);
      setMoodOptions(response.data);
    } catch (error) {
      console.error("Error fetching mood options:", error);
    }
  };

  const fetchMoods = async () => {
    try {
      const response = await axios.get(`${API}/moods`);
      setMoods(response.data);
    } catch (error) {
      console.error("Error fetching moods:", error);
    }
  };

  const handleSubmitMood = async (e) => {
    e.preventDefault();
    if (!selectedMood) return;

    setLoading(true);
    try {
      await axios.post(`${API}/moods`, {
        mood_emoji: selectedMood,
        mood_name: moodOptions[selectedMood],
        notes: notes
      });
      
      setSelectedMood("");
      setNotes("");
      fetchMoods();
      alert("Mood recorded successfully! 🎉");
    } catch (error) {
      console.error("Error submitting mood:", error);
      alert("Error recording mood. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.get(`${API}/moods/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'mood_history.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error exporting data:", error);
      alert("Error exporting data. Please try again.");
    }
  };

  const deleteMood = async (moodId) => {
    if (window.confirm("Are you sure you want to delete this mood entry?")) {
      try {
        await axios.delete(`${API}/moods/${moodId}`);
        fetchMoods();
      } catch (error) {
        console.error("Error deleting mood:", error);
        alert("Error deleting mood. Please try again.");
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " at " + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

  const groupMoodsByDate = (moods) => {
    const grouped = {};
    moods.forEach(mood => {
      const date = new Date(mood.timestamp).toDateString();
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(mood);
    });
    return grouped;
  };

  const getMoodStats = () => {
    const stats = {};
    moods.forEach(mood => {
      stats[mood.mood_name] = (stats[mood.mood_name] || 0) + 1;
    });
    return stats;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-800 text-center">
            🌈 Mood Tracker
          </h1>
          <p className="text-gray-600 text-center mt-2">
            Track your daily emotions and discover patterns
          </p>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex justify-center space-x-2 bg-white rounded-lg p-2 shadow-sm">
          <button
            onClick={() => setView("entry")}
            className={`px-4 py-2 rounded-md transition-colors ${
              view === "entry" 
                ? "bg-blue-500 text-white" 
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            📝 Add Mood
          </button>
          <button
            onClick={() => setView("history")}
            className={`px-4 py-2 rounded-md transition-colors ${
              view === "history" 
                ? "bg-blue-500 text-white" 
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            📊 History
          </button>
          <button
            onClick={() => setView("calendar")}
            className={`px-4 py-2 rounded-md transition-colors ${
              view === "calendar" 
                ? "bg-blue-500 text-white" 
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            📅 Calendar
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 pb-8">
        {/* Mood Entry Form */}
        {view === "entry" && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
              How are you feeling right now?
            </h2>
            
            <form onSubmit={handleSubmitMood} className="space-y-6">
              {/* Mood Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Select your mood:
                </label>
                <div className="grid grid-cols-5 gap-4">
                  {Object.entries(moodOptions).map(([emoji, name]) => (
                    <button
                      key={emoji}
                      type="button"
                      onClick={() => setSelectedMood(emoji)}
                      className={`p-4 rounded-xl border-2 transition-all hover:scale-105 ${
                        selectedMood === emoji
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="text-3xl mb-2">{emoji}</div>
                      <div className="text-xs text-gray-600">{name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (optional):
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="What's on your mind? Any thoughts about your mood..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows="3"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!selectedMood || loading}
                className="w-full bg-blue-500 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Recording..." : "Record Mood 🎯"}
              </button>
            </form>
          </div>
        )}

        {/* History View */}
        {view === "history" && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-semibold text-gray-800">
                  Mood History
                </h2>
                <button
                  onClick={handleExport}
                  className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
                >
                  📥 Export CSV
                </button>
              </div>

              {/* Stats */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-700 mb-3">Mood Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {Object.entries(getMoodStats()).map(([mood, count]) => (
                    <div key={mood} className="bg-gray-50 rounded-lg p-3 text-center">
                      <div className="text-sm text-gray-600">{mood}</div>
                      <div className="text-lg font-semibold text-blue-600">{count}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Mood List */}
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {moods.map((mood) => (
                  <div key={mood.id} className="flex items-start justify-between bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">{mood.mood_emoji}</div>
                      <div>
                        <div className="font-medium text-gray-800">{mood.mood_name}</div>
                        <div className="text-sm text-gray-600">{formatDate(mood.timestamp)}</div>
                        {mood.notes && (
                          <div className="text-sm text-gray-700 mt-1 italic">"{mood.notes}"</div>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => deleteMood(mood.id)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Calendar View */}
        {view === "calendar" && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Calendar View
            </h2>
            
            {Object.entries(groupMoodsByDate(moods)).map(([date, dayMoods]) => (
              <div key={date} className="mb-6 bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-3">{date}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {dayMoods.map((mood) => (
                    <div key={mood.id} className="flex items-center space-x-3 bg-white rounded-lg p-3">
                      <div className="text-xl">{mood.mood_emoji}</div>
                      <div className="flex-1">
                        <div className="font-medium text-sm">{mood.mood_name}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(mood.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                        {mood.notes && (
                          <div className="text-xs text-gray-600 mt-1">"{mood.notes}"</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            
            {moods.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                No mood entries yet. Start tracking your moods! 🌟
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;