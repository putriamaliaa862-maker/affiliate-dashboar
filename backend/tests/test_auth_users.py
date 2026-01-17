"""
Automated tests for Authentication and User Management endpoints.

Run: pytest tests/test_auth_users.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.auth.jwt import get_password_hash

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup test database before tests and cleanup after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def super_admin_user():
    """Create a super admin user for testing"""
    from app.models.user import User
    
    db = TestingSessionLocal()
    user = User(
        username="test_superadmin",
        email="superadmin@test.com",
        password_hash=get_password_hash("SuperAdmin123!"),
        full_name="Test Super Admin",
        role="super_admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()
    
    yield {"id": user_id, "username": "test_superadmin", "password": "SuperAdmin123!"}
    
    # Cleanup
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


@pytest.fixture
def admin_user():
    """Create an admin user for testing"""
    from app.models.user import User
    
    db = TestingSessionLocal()
    user = User(
        username="test_admin",
        email="admin@test.com",
        password_hash=get_password_hash("Admin123!"),
        full_name="Test Admin",
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()
    
    yield {"id": user_id, "username": "test_admin", "password": "Admin123!"}
    
    # Cleanup
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


@pytest.fixture
def leader_user():
    """Create a leader user for testing"""
    from app.models.user import User
    
    db = TestingSessionLocal()
    user = User(
        username="test_leader",
        email="leader@test.com",
        password_hash=get_password_hash("Leader123!"),
        full_name="Test Leader",
        role="leader",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()
    
    yield {"id": user_id, "username": "test_leader", "password": "Leader123!"}
    
    # Cleanup
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


@pytest.fixture
def affiliate_user(leader_user):
    """Create an affiliate user for testing"""
    from app.models.user import User
    
    db = TestingSessionLocal()
    user = User(
        username="test_affiliate",
        email="affiliate@test.com",
        password_hash=get_password_hash("Affiliate123!"),
        full_name="Test Affiliate",
        role="affiliate",
        leader_id=leader_user["id"],
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()
    
    yield {"id": user_id, "username": "test_affiliate", "password": "Affiliate123!", "leader_id": leader_user["id"]}
    
    # Cleanup
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


def get_auth_header(username: str, password: str):
    """Helper function to get authorization header"""
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ========================================
# AUTHENTICATION TESTS
# ========================================

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self, super_admin_user):
        """Test successful login with valid credentials"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": super_admin_user["username"],
                "password": super_admin_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == super_admin_user["username"]
        assert data["user"]["role"] == "super_admin"
    
    def test_login_with_email(self, super_admin_user):
        """Test login using email instead of username"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "superadmin@test.com",  # Using email
                "password": super_admin_user["password"]
            }
        )
        assert response.status_code == 200
    
    def test_login_invalid_password(self, super_admin_user):
        """Test login with incorrect password"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": super_admin_user["username"],
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent username"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "Password123!"
            }
        )
        assert response.status_code == 401
    
    def test_login_inactive_user(self):
        """Test login with inactive user account"""
        from app.models.user import User
        
        # Create inactive user
        db = TestingSessionLocal()
        user = User(
            username="inactive_user",
            email="inactive@test.com",
            password_hash=get_password_hash("Password123!"),
            role="affiliate",
            is_active=False  # Inactive
        )
        db.add(user)
        db.commit()
        db.close()
        
        response = client.post(
            "/api/auth/login",
            json={
                "username": "inactive_user",
                "password": "Password123!"
            }
        )
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()
    
    def test_refresh_token(self, super_admin_user):
        """Test refresh token flow"""
        # Login to get tokens
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": super_admin_user["username"],
                "password": super_admin_user["password"]
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self):
        """Test refresh token with invalid token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, super_admin_user):
        """Test get current user info endpoint"""
        headers = get_auth_header(super_admin_user["username"], super_admin_user["password"])
        
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == super_admin_user["username"]
        assert data["role"] == "super_admin"
    
    def test_get_current_user_unauthorized(self):
        """Test get current user without authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # No auth header
    
    def test_logout(self, super_admin_user):
        """Test logout endpoint"""
        headers = get_auth_header(super_admin_user["username"], super_admin_user["password"])
        
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()


# ========================================
# USER MANAGEMENT TESTS
# ========================================

class TestUserCreation:
    """Test user creation endpoint"""
    
    def test_create_user_as_admin(self, admin_user):
        """Test creating a user as admin"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "NewUser123!",
                "full_name": "New User",
                "role": "affiliate",
                "leader_id": admin_user["id"]  # Admin can be a leader
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "affiliate"
    
    def test_create_user_password_validation(self, admin_user):
        """Test password strength validation"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        # Password too short
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "testuser1",
                "email": "test1@test.com",
                "password": "Short1",  # Only 6 chars
                "role": "affiliate",
                "leader_id": admin_user["id"]
            }
        )
        assert response.status_code == 422  # Validation error
        
        # Password without uppercase
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "testuser2",
                "email": "test2@test.com",
                "password": "nouppercase123",
                "role": "affiliate",
                "leader_id": admin_user["id"]
            }
        )
        assert response.status_code == 422
        
        # Password without digit
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "testuser3",
                "email": "test3@test.com",
                "password": "NoDigitHere",
                "role": "affiliate",
                "leader_id": admin_user["id"]
            }
        )
        assert response.status_code == 422
    
    def test_create_affiliate_without_leader(self, admin_user):
        """Test that affiliate creation requires leader_id"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "affiliate_no_leader",
                "email": "noLeader@test.com",
                "password": "Password123!",
                "role": "affiliate"
                # Missing leader_id
            }
        )
        assert response.status_code == 422
    
    def test_create_user_duplicate_username(self, admin_user):
        """Test creating user with duplicate username"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        # Create first user
        client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "duplicate_user",
                "email": "user1@test.com",
                "password": "Password123!",
                "role": "leader"
            }
        )
        
        # Try to create user with same username
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "duplicate_user",  # Duplicate
                "email": "user2@test.com",
                "password": "Password123!",
                "role": "leader"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_create_user_as_affiliate_denied(self, affiliate_user):
        """Test that affiliates cannot create users"""
        headers = get_auth_header(affiliate_user["username"], affiliate_user["password"])
        
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "shouldfail",
                "email": "fail@test.com",
                "password": "Password123!",
                "role": "affiliate",
                "leader_id": affiliate_user["leader_id"]
            }
        )
        assert response.status_code == 403  # Forbidden


class TestUserRetrieval:
    """Test user retrieval endpoints"""
    
    def test_list_users_as_admin(self, admin_user, leader_user, affiliate_user):
        """Test listing all users as admin"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 3  # At least admin, leader, affiliate
    
    def test_list_users_as_leader(self, leader_user, affiliate_user):
        """Test that leaders can only see their team"""
        headers = get_auth_header(leader_user["username"], leader_user["password"])
        
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        users = response.json()
        
        # Should only see themselves and their affiliates
        usernames = [u["username"] for u in users]
        assert leader_user["username"] in usernames
        assert affiliate_user["username"] in usernames
    
    def test_list_users_with_filters(self, admin_user):
        """Test filtering users"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        # Filter by role
        response = client.get("/api/users?role=admin", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert all(u["role"] == "admin" for u in users)
        
        # Filter by active status
        response = client.get("/api/users?is_active=true", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert all(u["is_active"] is True for u in users)
        
        # Search
        response = client.get(f"/api/users?search={admin_user['username']}", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert any(admin_user["username"] in u["username"] for u in users)
    
    def test_get_user_by_id(self, admin_user, leader_user):
        """Test getting specific user"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.get(f"/api/users/{leader_user['id']}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == leader_user["id"]
        assert data["username"] == leader_user["username"]
    
    def test_get_user_access_control(self, affiliate_user, leader_user):
        """Test that affiliates can only view themselves"""
        headers = get_auth_header(affiliate_user["username"], affiliate_user["password"])
        
        # Can view self
        response = client.get(f"/api/users/{affiliate_user['id']}", headers=headers)
        assert response.status_code == 200
        
        # Cannot view leader
        response = client.get(f"/api/users/{leader_user['id']}", headers=headers)
        assert response.status_code == 403


class TestUserUpdate:
    """Test user update endpoint"""
    
    def test_update_user(self, admin_user, leader_user):
        """Test updating user information"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.put(
            f"/api/users/{leader_user['id']}",
            headers=headers,
            json={
                "full_name": "Updated Leader Name",
                "phone": "081234567890"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Leader Name"
        assert data["phone"] == "081234567890"
    
    def test_update_user_role(self, super_admin_user, leader_user):
        """Test changing user role"""
        headers = get_auth_header(super_admin_user["username"], super_admin_user["password"])
        
        response = client.put(
            f"/api/users/{leader_user['id']}",
            headers=headers,
            json={"role": "admin"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"


class TestUserDeletion:
    """Test user deletion endpoint"""
    
    def test_delete_user(self, super_admin_user, leader_user):
        """Test soft deleting a user"""
        headers = get_auth_header(super_admin_user["username"], super_admin_user["password"])
        
        response = client.delete(f"/api/users/{leader_user['id']}", headers=headers)
        assert response.status_code == 200
        
        # Verify user is inactive
        user_response = client.get(f"/api/users/{leader_user['id']}", headers=headers)
        assert user_response.json()["is_active"] is False
    
    def test_delete_self_denied(self, super_admin_user):
        """Test that users cannot delete themselves"""
        headers = get_auth_header(super_admin_user["username"], super_admin_user["password"])
        
        response = client.delete(f"/api/users/{super_admin_user['id']}", headers=headers)
        assert response.status_code == 400
        assert "cannot delete yourself" in response.json()["detail"].lower()
    
    def test_delete_user_requires_super_admin(self, admin_user, leader_user):
        """Test that only super admin can delete users"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.delete(f"/api/users/{leader_user['id']}", headers=headers)
        assert response.status_code == 403


class TestPasswordChange:
    """Test password change endpoint"""
    
    def test_change_own_password(self, leader_user):
        """Test user changing their own password"""
        headers = get_auth_header(leader_user["username"], leader_user["password"])
        
        response = client.post(
            f"/api/users/{leader_user['id']}/change-password",
            headers=headers,
            json={
                "current_password": leader_user["password"],
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code == 200
        
        # Verify new password works
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": leader_user["username"],
                "password": "NewPassword123!"
            }
        )
        assert login_response.status_code == 200
    
    def test_change_password_wrong_current(self, leader_user):
        """Test password change with wrong current password"""
        headers = get_auth_header(leader_user["username"], leader_user["password"])
        
        response = client.post(
            f"/api/users/{leader_user['id']}/change-password",
            headers=headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_admin_change_any_password(self, admin_user, affiliate_user):
        """Test that admins can change any user's password"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        # Admin changing affiliate's password (no current_password needed)
        response = client.post(
            f"/api/users/{affiliate_user['id']}/change-password",
            headers=headers,
            json={
                "current_password": "",  # Not required for admin
                "new_password": "NewAffiliatePass123!"
            }
        )
        assert response.status_code == 200


class TestRBAC:
    """Test Role-Based Access Control"""
    
    def test_role_hierarchy(self, super_admin_user, admin_user, leader_user, affiliate_user):
        """Test that role hierarchy is enforced"""
        # Super admin can access admin-only endpoint
        headers = get_auth_header(super_admin_user["username"], super_admin_user["password"])
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        
        # Admin can access leader-required endpoint
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        
        # Leader can access leader-required endpoint
        headers = get_auth_header(leader_user["username"], leader_user["password"])
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 200
        
        # Affiliate cannot access leader-required endpoint (create user)
        headers = get_auth_header(affiliate_user["username"], affiliate_user["password"])
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "test",
                "email": "test@test.com",
                "password": "Password123!",
                "role": "affiliate",
                "leader_id": leader_user["id"]
            }
        )
        assert response.status_code == 403
    
    def test_leader_assignment(self, admin_user, leader_user, affiliate_user):
        """Test assigning leader to affiliate"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        # Create new leader
        new_leader_response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": "new_leader",
                "email": "newleader@test.com",
                "password": "Leader123!",
                "role": "leader"
            }
        )
        new_leader_id = new_leader_response.json()["id"]
        
        # Assign new leader to affiliate
        response = client.post(
            f"/api/users/{affiliate_user['id']}/assign-leader",
            headers=headers,
            json={"leader_id": new_leader_id}
        )
        assert response.status_code == 200
        
        # Verify assignment
        user_response = client.get(f"/api/users/{affiliate_user['id']}", headers=headers)
        assert user_response.json()["leader_id"] == new_leader_id
    
    def test_get_team_members(self, leader_user, affiliate_user):
        """Test getting team members for a leader"""
        headers = get_auth_header(leader_user["username"], leader_user["password"])
        
        response = client.get(f"/api/users/{leader_user['id']}/team", headers=headers)
        assert response.status_code == 200
        team = response.json()
        
        # Should include the affiliate
        assert any(u["id"] == affiliate_user["id"] for u in team)


class TestActivityLogs:
    """Test activity logging"""
    
    def test_activity_log_on_login(self, admin_user):
        """Test that login creates activity log"""
        # Login
        client.post(
            "/api/auth/login",
            json={
                "username": admin_user["username"],
                "password": admin_user["password"]
            }
        )
        
        # Check activity logs
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        response = client.get(f"/api/activity-logs/user/{admin_user['id']}", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        
        # Should have login_success log
        assert any(log["action"] == "login_success" for log in logs)
    
    def test_view_activity_logs_as_admin(self, admin_user):
        """Test viewing all activity logs as admin"""
        headers = get_auth_header(admin_user["username"], admin_user["password"])
        
        response = client.get("/api/activity-logs", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
    
    def test_view_own_activity_logs(self, leader_user):
        """Test that users can view their own activity logs"""
        headers = get_auth_header(leader_user["username"], leader_user["password"])
        
        response = client.get(f"/api/activity-logs/user/{leader_user['id']}", headers=headers)
        assert response.status_code == 200
        logs = response.json()
        assert all(log["user_id"] == leader_user["id"] for log in logs)
    
    def test_cannot_view_others_logs(self, affiliate_user, leader_user):
        """Test that users cannot view other users' logs"""
        headers = get_auth_header(affiliate_user["username"], affiliate_user["password"])
        
        response = client.get(f"/api/activity-logs/user/{leader_user['id']}", headers=headers)
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
