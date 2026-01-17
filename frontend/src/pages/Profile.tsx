import React from 'react'
import { useAuth } from '@/hooks/useAuth'
import { getRoleBadgeColor } from '@/utils/permissions'

const Profile: React.FC = () => {
    const { user } = useAuth()

    if (!user) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-500">Loading profile...</div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-800">My Profile</h1>

            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center space-x-6 mb-6">
                    <div className="h-20 w-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white text-3xl font-semibold">
                        {user.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">
                            {user.full_name || user.username}
                        </h2>
                        <p className="text-gray-500">@{user.username}</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="border-t pt-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-gray-500">Email</label>
                                <p className="mt-1 text-gray-900">{user.email}</p>
                            </div>

                            <div>
                                <label className="text-sm font-medium text-gray-500">Role</label>
                                <div className="mt-1">
                                    <span className={`px-3 py-1 rounded text-sm font-semibold ${getRoleBadgeColor(user.role)}`}>
                                        {user.role.replace('_', ' ').toUpperCase()}
                                    </span>
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-medium text-gray-500">Username</label>
                                <p className="mt-1 text-gray-900">{user.username}</p>
                            </div>

                            <div>
                                <label className="text-sm font-medium text-gray-500">Account Status</label>
                                <p className="mt-1">
                                    <span className="px-3 py-1 rounded text-sm font-semibold bg-green-100 text-green-800">
                                        Active
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="border-t pt-4 mt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
                        <div className="space-x-4">
                            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                Edit Profile
                            </button>
                            <button className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
                                Change Password
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Profile
