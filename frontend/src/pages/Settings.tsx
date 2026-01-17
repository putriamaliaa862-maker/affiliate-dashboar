import React, { useState } from 'react'

const Settings: React.FC = () => {
    const [notifications, setNotifications] = useState(true)
    const [emailAlerts, setEmailAlerts] = useState(false)

    const handleSave = () => {
        alert('Settings saved successfully!')
    }

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-800">Settings</h1>

            <div className="bg-white rounded-lg shadow p-6 space-y-6">
                {/* Notification Settings */}
                <div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Notifications</h2>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <label className="font-medium text-gray-700">Push Notifications</label>
                                <p className="text-sm text-gray-500">Receive push notifications for important updates</p>
                            </div>
                            <button
                                onClick={() => setNotifications(!notifications)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${notifications ? 'bg-blue-600' : 'bg-gray-200'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${notifications ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <label className="font-medium text-gray-700">Email Alerts</label>
                                <p className="text-sm text-gray-500">Receive email notifications for critical events</p>
                            </div>
                            <button
                                onClick={() => setEmailAlerts(!emailAlerts)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${emailAlerts ? 'bg-blue-600' : 'bg-gray-200'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${emailAlerts ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Appearance */}
                <div className="border-t pt-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Appearance</h2>

                    <div>
                        <label className="font-medium text-gray-700 block mb-2">Theme</label>
                        <select className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <option>Light</option>
                            <option>Dark</option>
                            <option>Auto</option>
                        </select>
                    </div>
                </div>

                {/* Language */}
                <div className="border-t pt-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Language</h2>

                    <div>
                        <label className="font-medium text-gray-700 block mb-2">Display Language</label>
                        <select className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <option>English</option>
                            <option>Bahasa Indonesia</option>
                        </select>
                    </div>
                </div>

                {/* Save Button */}
                <div className="border-t pt-6">
                    <button
                        onClick={handleSave}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                    >
                        Save Settings
                    </button>
                </div>
            </div>
        </div>
    )
}

export default Settings
