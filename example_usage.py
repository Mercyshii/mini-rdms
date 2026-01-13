"""
Example Usage of Simple RDBMS
Demonstrates basic database operations programmatically
"""

from database_engine import DatabaseEngine

def main():
    """Demonstrate the RDBMS with various operations"""
    
    print("🚀 Simple RDBMS Example Usage")
    print("=" * 50)
    
    # Initialize database engine
    engine = DatabaseEngine()
    
    # 1. Create tables
    print("\n📝 Creating tables...")
    
    # Users table
    result = engine.execute("""
        CREATE TABLE users (
            id INT PRIMARY_KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """)
    print(f"Users table: {result.message}")
    
    # Posts table
    result = engine.execute("""
        CREATE TABLE posts (
            id INT PRIMARY_KEY,
            title TEXT NOT NULL,
            content TEXT,
            user_id INT
        )
    """)
    print(f"Posts table: {result.message}")
    
    # 2. Insert data
    print("\n📥 Inserting sample data...")
    
    users_data = [
        "INSERT INTO users (id, name, email) VALUES (1, 'Alice Johnson', 'alice@example.com')",
        "INSERT INTO users (id, name, email) VALUES (2, 'Bob Smith', 'bob@example.com')",
        "INSERT INTO users (id, name, email) VALUES (3, 'Carol Davis', 'carol@example.com')"
    ]
    
    posts_data = [
        "INSERT INTO posts (id, title, content, user_id) VALUES (1, 'Hello World', 'My first post!', 1)",
        "INSERT INTO posts (id, title, content, user_id) VALUES (2, 'Database Design', 'Thoughts on RDBMS architecture', 1)",
        "INSERT INTO posts (id, title, content, user_id) VALUES (3, 'Python Tips', 'Useful Python tricks', 2)",
        "INSERT INTO posts (id, title, content, user_id) VALUES (4, 'Web Development', 'Building web apps with Flask', 3)"
    ]
    
    for sql in users_data + posts_data:
        result = engine.execute(sql)
        print(f"  {result.message}")
    
    # 3. Query operations
    print("\n🔍 Querying data...")
    
    # Select all users
    result = engine.execute("SELECT * FROM users")
    print("\nAll users:")
    for row in result.data:
        print(f"  ID: {row['id']}, Name: {row['name']}, Email: {row['email']}")
    
    # Select posts by specific user
    result = engine.execute("SELECT * FROM posts WHERE user_id = 1")
    print(f"\nPosts by Alice (ID: 1):")
    for row in result.data:
        print(f"  {row['title']}: {row['content'][:30]}...")
    
    # 4. JOIN operations (simplified manual join)
    print("\n🔗 JOIN operations...")
    
    users_result = engine.execute("SELECT * FROM users")
    posts_result = engine.execute("SELECT * FROM posts")
    
    print("\nUsers and their posts:")
    for user in users_result.data:
        user_posts = [post for post in posts_result.data if post['user_id'] == user['id']]
        for post in user_posts:
            print(f"  {user['name']} wrote: {post['title']}")
    
    # 5. Update operations
    print("\n✏️ Updating data...")
    
    result = engine.execute("UPDATE users SET name = 'Alice Smith' WHERE id = 1")
    print(f"Update result: {result.message}")
    
    # Verify update
    result = engine.execute("SELECT name FROM users WHERE id = 1")
    print(f"Alice's new name: {result.data[0]['name']}")
    
    # 6. Delete operations
    print("\n🗑️ Deleting data...")
    
    result = engine.execute("DELETE FROM posts WHERE id = 4")
    print(f"Delete result: {result.message}")
    
    # Show remaining posts
    result = engine.execute("SELECT * FROM posts")
    print(f"Remaining posts: {len(result.data)}")
    
    # 7. Constraint violations
    print("\n⚠️ Testing constraint violations...")
    
    # Try to insert duplicate primary key
    result = engine.execute("INSERT INTO users (id, name, email) VALUES (1, 'Dave', 'dave@example.com')")
    print(f"Duplicate primary key: {result.message}")
    
    # Try to insert duplicate email
    result = engine.execute("INSERT INTO users (id, name, email) VALUES (4, 'Dave', 'alice@example.com')")
    print(f"Duplicate email: {result.message}")
    
    # Try to insert NULL in NOT NULL column
    result = engine.execute("INSERT INTO users (id, name, email) VALUES (4, NULL, 'dave@example.com')")
    print(f"NULL in NOT NULL column: {result.message}")
    
    # 8. Complex queries
    print("\n🎯 Complex queries...")
    
    # Count posts per user
    print("\nPosts per user:")
    users_result = engine.execute("SELECT * FROM users")
    for user in users_result.data:
        posts_result = engine.execute(f"SELECT * FROM posts WHERE user_id = {user['id']}")
        count = len(posts_result.data)
        print(f"  {user['name']}: {count} posts")
    
    # 9. Database statistics
    print("\n📊 Database statistics:")
    
    # List tables manually since .tables isn't supported in engine
    print("Tables: users, posts")
    
    for table_name in ['users', 'posts']:
        result = engine.execute(f"SELECT * FROM {table_name}")
        print(f"{table_name.capitalize()}: {len(result.data)} rows")
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    main()
