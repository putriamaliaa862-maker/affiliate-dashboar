import React, { useState } from 'react'

interface UserFormProps {
    user?: {
        id: number
        username: string
        email: string
        full_name?: string
        phone?: string
        role: string
        leader_id?: number
    }
    onSubmit: (data: UserFormData) => Promise<void>
    onCancel: () => void
}

export interface UserFormData {
    username: string
    email: string
    full_name?: string
    phone?: string
    password?: string
    role: string
    leader_id?: number
}

const UserForm: React.FC<UserFormProps> = ({ user, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState<UserFormData>({
        username: user?.username || '',
        email: user?.email || '',
        full_name: user?.full_name || '',
        phone: user?.phone || '',
        password: '',
        role: user?.role || 'affiliate',
        leader_id: user?.leader_id || undefined,
    })

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            // Validation
            if (!formData.username || !formData.email) {
                throw new Error('Username and email are required')
            }

            if (!user && !formData.password) {
                throw new Error('Password is required for new users')
            }

            if (formData.password && formData.password.length < 8) {
                throw new Error('Password must be at least 8 characters')
            }

            if (formData.role === 'affiliate' && !formData.leader_id) {
                throw new Error('Affiliates must be assigned to a leader')
            }

            await onSubmit(formData)
        } catch (err: any) {
            setError(err.message || 'Failed to save user')
        } finally {
            setLoading(false)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
                <div className="bg-red-50 border border-red-200 rounded p-3">
                    <p className="text-red-600 text-sm">{error}</p>
                </div>
            )}

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username *
                </label>
                <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    disabled={!!user} // Username cannot be changed
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                </label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                </label>
                <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                </label>
                <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>

            {!user && (
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Password *
                    </label>
                    <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                        minLength={8}
                        placeholder="Minimum 8 characters"
                    />
                </div>
            )}

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role *
                </label>
                <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                >
                    <option value="affiliate">Affiliate</option>
                    <option value="leader">Leader</option>
                    <option value="admin">Admin</option>
                    <option value="super_admin">Super Admin</option>
                </select>
            </div>

            {formData.role === 'affiliate' && (
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Leader ID * (for affiliates)
                    </label>
                    <input
                        type="number"
                        name="leader_id"
                        value={formData.leader_id || ''}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                        placeholder="Enter leader's user ID"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                        Note: In production, this should be a dropdown of available leaders
                    </p>
                </div>
            )}

            <div className="flex gap-3 pt-4">
                <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold"
                >
                    {loading ? 'Saving...' : user ? 'Update User' : 'Create User'}
                </button>
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={loading}
                    className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 font-semibold"
                >
                    Cancel
                </button>
            </div>
        </form>
    )
}

export default UserForm
