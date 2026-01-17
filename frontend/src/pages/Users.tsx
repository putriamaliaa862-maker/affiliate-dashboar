import React, { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import api from '@/api/client'
import Modal from '@/components/Modal'
import UserForm, { UserFormData } from '@/components/forms/UserForm'

interface User {
    id: number
    username: string
    email: string
    full_name?: string
    role: string
    is_active: boolean
    created_at: string
}

const Users: React.FC = () => {
    const { user: currentUser } = useAuth()
    const [users, setUsers] = useState<User[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [selectedUser, setSelectedUser] = useState<User | undefined>()

    useEffect(() => {
        fetchUsers()
    }, [])

    const fetchUsers = async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await api.get('/users')
            setUsers(response.data)
        } catch (err: any) {
            console.error('Failed to fetch users:', err)
            setError(err.response?.data?.detail || 'Failed to load users')
        } finally {
            setLoading(false)
        }
    }

    const handleAddUser = () => {
        setSelectedUser(undefined)
        setIsModalOpen(true)
    }

    const handleEditUser = (user: User) => {
        setSelectedUser(user)
        setIsModalOpen(true)
    }

    const handleSubmit = async (data: UserFormData) => {
        try {
            if (selectedUser) {
                // UPDATE existing user
                await api.put(`/users/${selectedUser.id}`, {
                    email: data.email,
                    full_name: data.full_name,
                    phone: data.phone,
                    role: data.role,
                    leader_id: data.leader_id,
                })
            } else {
                // CREATE new user
                await api.post('/users', {
                    username: data.username,
                    email: data.email,
                    full_name: data.full_name,
                    phone: data.phone,
                    password: data.password,
                    role: data.role,
                    leader_id: data.leader_id,
                })
            }
            setIsModalOpen(false)
            fetchUsers() // Refresh list
        } catch (error: any) {
            console.error('Failed to save user:', error)
            throw new Error(
                error.response?.data?.detail || 'Failed to save user. Please try again.'
            )
        }
    }

    const handleDelete = async (user: User) => {
        if (user.id === currentUser?.id) {
            alert('You cannot delete yourself!')
            return
        }

        if (!confirm(`Are you sure you want to delete user "${user.username}"? This will deactivate their account.`)) {
            return
        }

        try {
            await api.delete(`/users/${user.id}`)
            fetchUsers() // Refresh list
        } catch (error: any) {
            console.error('Failed to delete user:', error)
            alert(error.response?.data?.detail || 'Failed to delete user. Please try again.')
        }
    }

    const getRoleBadgeColor = (role: string) => {
        const colors = {
            super_admin: 'bg-purple-100 text-purple-800',
            admin: 'bg-blue-100 text-blue-800',
            leader: 'bg-green-100 text-green-800',
            affiliate: 'bg-gray-100 text-gray-800',
        }
        return colors[role as keyof typeof colors] || 'bg-gray-100 text-gray-800'
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-500">Loading users...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600">{error}</p>
                <button
                    onClick={fetchUsers}
                    className="mt-2 text-red-700 hover:text-red-900 underline"
                >
                    Try again
                </button>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-3xl font-bold text-gray-800">Manajemen User</h1>
                        <div className="group relative">
                            <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
                            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                                Biar aman, atur akses sesuai jobdesk.
                            </div>
                        </div>
                    </div>
                    <p className="text-gray-500">Atur siapa aja yang bisa masuk dashboard, kasih akses sesuai role.</p>
                </div>
                <button
                    onClick={handleAddUser}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                    Add User
                </button>
            </div>

            {users.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                    No users found. Click "Add User" to create one.
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    User
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Email
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Role
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0 h-10 w-10">
                                                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                                                    {user.username.charAt(0).toUpperCase()}
                                                </div>
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {user.full_name || user.username}
                                                </div>
                                                <div className="text-sm text-gray-500">@{user.username}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{user.email}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-xs font-semibold ${getRoleBadgeColor(user.role)}`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-xs font-semibold ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                            }`}>
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm">
                                        <button
                                            onClick={() => handleEditUser(user)}
                                            className="text-blue-600 hover:text-blue-900 mr-3"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDelete(user)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={selectedUser ? 'Edit User' : 'Create New User'}
            >
                <UserForm
                    user={selectedUser}
                    onSubmit={handleSubmit}
                    onCancel={() => setIsModalOpen(false)}
                />
            </Modal>
        </div>
    )
}

export default Users
