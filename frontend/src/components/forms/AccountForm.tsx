import React, { useState } from 'react'
import { ShopeeAccount } from '@/types'

interface AccountFormProps {
    account?: ShopeeAccount
    studioId?: number
    onSubmit: (data: Partial<ShopeeAccount>) => void
    onCancel: () => void
}

const AccountForm: React.FC<AccountFormProps> = ({ account, studioId, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
        studio_id: account?.studio_id || studioId || 1,
        account_name: account?.account_name || '',
        shopee_account_id: account?.shopee_account_id || '',
        access_token: (account as any)?.access_token || '',
        refresh_token: (account as any)?.refresh_token || '',
        is_active: account?.is_active ?? true,
    })

    const [cookieInput, setCookieInput] = useState('')

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target
        const checked = (e.target as HTMLInputElement).checked
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }))
    }

    const handleCookieImport = () => {
        // Parse cookies from textarea (format: SPC_EC=xxx; SPC_F=yyy)
        const cookies = cookieInput.split(';').map(c => c.trim())
        let accessToken = ''
        let refreshToken = ''

        cookies.forEach(cookie => {
            const [name, value] = cookie.split('=').map(s => s.trim())
            if (name === 'SPC_EC' || name === 'access_token') {
                accessToken = value
            }
            if (name === 'SPC_F' || name === 'refresh_token') {
                refreshToken = value
            }
        })

        setFormData(prev => ({
            ...prev,
            access_token: accessToken || prev.access_token,
            refresh_token: refreshToken || prev.refresh_token
        }))

        setCookieInput('')
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        onSubmit(formData)
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            {/* Import dari Cookie */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">📥 Import dari Extension</h3>
                <p className="text-xs text-blue-700 mb-3">
                    Paste cookie dari Shopee (SPC_EC, SPC_F) yang didapat dari extension
                </p>
                <textarea
                    value={cookieInput}
                    onChange={(e) => setCookieInput(e.target.value)}
                    rows={3}
                    placeholder="SPC_EC=xxx; SPC_F=yyy; ..."
                    className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs mb-2"
                />
                <button
                    type="button"
                    onClick={handleCookieImport}
                    className="w-full bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
                >
                    Import Cookies
                </button>
            </div>

            <div className="border-t pt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Atau Tambah Manual</h3>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Account Name *</label>
                    <input
                        type="text"
                        name="account_name"
                        value={formData.account_name}
                        onChange={handleChange}
                        required
                        placeholder="e.g., Toko Utama Jakarta"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Shopee Account ID *</label>
                    <input
                        type="text"
                        name="shopee_account_id"
                        value={formData.shopee_account_id}
                        onChange={handleChange}
                        required
                        placeholder="Shopee Live Account ID"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        ID dari akun Shopee Live yang akan digunakan
                    </p>
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
                    <textarea
                        name="access_token"
                        value={formData.access_token}
                        onChange={handleChange}
                        rows={2}
                        placeholder="Auto-filled from extension or paste here"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Refresh Token</label>
                    <textarea
                        name="refresh_token"
                        value={formData.refresh_token}
                        onChange={handleChange}
                        rows={2}
                        placeholder="Auto-filled from extension or paste here"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
                    />
                </div>

                <div className="flex items-center mb-4">
                    <input
                        type="checkbox"
                        name="is_active"
                        checked={formData.is_active}
                        onChange={handleChange}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label className="ml-2 text-sm text-gray-700">Active</label>
                </div>
            </div>

            <div className="flex gap-3 pt-4">
                <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium"
                >
                    {account ? 'Update' : 'Add'} Account
                </button>
                <button
                    type="button"
                    onClick={onCancel}
                    className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 font-medium"
                >
                    Cancel
                </button>
            </div>
        </form>
    )
}

export default AccountForm
