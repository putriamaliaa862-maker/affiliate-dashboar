import React, { useState, useEffect } from 'react'
import { Copy, RefreshCw, Key, AlertCircle } from 'lucide-react'
import authApi from '@/api/auth'

const Settings: React.FC = () => {
    const [notifications, setNotifications] = useState(true)
    const [emailAlerts, setEmailAlerts] = useState(false)

    // Access Code state
    const [accessCode, setAccessCode] = useState<string | null>(null)
    const [loadingCode, setLoadingCode] = useState(false)
    const [generatingCode, setGeneratingCode] = useState(false)
    const [copySuccess, setCopySuccess] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Load access code on mount
    useEffect(() => {
        loadAccessCode()
    }, [])

    const loadAccessCode = async () => {
        try {
            setLoadingCode(true)
            setError(null)
            const response = await authApi.getMyAccessCode()
            setAccessCode(response.access_code)
        } catch (err: any) {
            console.error('Failed to load access code:', err)
            setError('Gagal memuat access code')
        } finally {
            setLoadingCode(false)
        }
    }

    const handleGenerateCode = async () => {
        try {
            setGeneratingCode(true)
            setError(null)
            const response = await authApi.regenerateAccessCode()
            setAccessCode(response.access_code)
        } catch (err: any) {
            console.error('Failed to generate access code:', err)
            setError('Gagal generate access code')
        } finally {
            setGeneratingCode(false)
        }
    }

    const handleCopyCode = async () => {
        if (!accessCode) return

        try {
            await navigator.clipboard.writeText(accessCode)
            setCopySuccess(true)
            setTimeout(() => setCopySuccess(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    const handleSave = () => {
        alert('Settings saved successfully!')
    }

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-800">Settings</h1>

            <div className="bg-white rounded-lg shadow p-6 space-y-6">
                {/* Access Code Section */}
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Key className="w-5 h-5 text-purple-600" />
                        <h2 className="text-xl font-semibold text-gray-900">Access Code Extension 🔌</h2>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">
                        Kode ini dipakai buat nyambungin extension ke dashboard kamu.
                    </p>

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-sm">{error}</span>
                        </div>
                    )}

                    <div className="space-y-3">
                        {/* Access Code Display */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Your Access Code
                            </label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={accessCode || 'Belum ada code, generate dulu ya!'}
                                    readOnly
                                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-lg tracking-wider"
                                />
                                <button
                                    onClick={handleCopyCode}
                                    disabled={!accessCode || loadingCode}
                                    className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${copySuccess
                                            ? 'bg-green-600 text-white'
                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                                    title="Copy to clipboard"
                                >
                                    <Copy className="w-4 h-4" />
                                    {copySuccess ? 'Copied!' : 'Copy'}
                                </button>
                            </div>
                        </div>

                        {/* Generate Button */}
                        <button
                            onClick={handleGenerateCode}
                            disabled={generatingCode || loadingCode}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
                        >
                            <RefreshCw className={`w-4 h-4 ${generatingCode ? 'animate-spin' : ''}`} />
                            {generatingCode ? 'Generating...' : accessCode ? 'Reset Code' : 'Generate Code'}
                        </button>

                        {/* Warning */}
                        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                            <p className="text-sm text-amber-800">
                                ⚠️ Jangan share ke orang lain ya bro! 🙏 Code ini ngasih akses ke akun kamu.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Notification Settings */}
                <div className="border-t pt-6">
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
