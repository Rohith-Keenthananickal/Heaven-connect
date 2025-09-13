"""
Migration script to create training module tables
Run this script to create the training module tables in the database
"""

import asyncio
from sqlalchemy import text
from app.database import engine


async def create_training_tables():
    """Create training module tables"""
    
    # SQL statements to create training tables
    create_tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS training_modules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            module_order INT NOT NULL DEFAULT 0 COMMENT 'Order of module in sequence',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            estimated_duration_minutes INT COMMENT 'Estimated time to complete in minutes',
            created_by INT NOT NULL COMMENT 'Admin who created this module',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_module_order (module_order),
            INDEX idx_is_active (is_active),
            INDEX idx_created_by (created_by),
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        
        """
        CREATE TABLE IF NOT EXISTS training_contents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            module_id INT NOT NULL,
            content_type ENUM('TEXT', 'VIDEO', 'DOCUMENT', 'QUIZ') NOT NULL,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL COMMENT 'Text content or video/document URL',
            content_order INT NOT NULL DEFAULT 0 COMMENT 'Order within the module',
            is_required BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Whether this content is required to complete the module',
            video_duration_seconds INT COMMENT 'Duration in seconds for video content',
            thumbnail_url VARCHAR(500) COMMENT 'Thumbnail URL for video content',
            quiz_questions JSON COMMENT 'Quiz questions and answers in JSON format',
            passing_score INT COMMENT 'Minimum score required to pass (percentage)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_module_id (module_id),
            INDEX idx_content_type (content_type),
            INDEX idx_content_order (content_order),
            FOREIGN KEY (module_id) REFERENCES training_modules(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """,
        
        """
        CREATE TABLE IF NOT EXISTS training_progress (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL COMMENT 'Area Coordinator user ID',
            module_id INT NOT NULL,
            content_id INT COMMENT 'Specific content progress (optional)',
            status ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED') NOT NULL DEFAULT 'NOT_STARTED',
            progress_percentage INT NOT NULL DEFAULT 0 COMMENT 'Progress percentage (0-100)',
            time_spent_seconds INT NOT NULL DEFAULT 0 COMMENT 'Time spent in seconds',
            quiz_score INT COMMENT 'Quiz score (percentage)',
            quiz_attempts INT NOT NULL DEFAULT 0 COMMENT 'Number of quiz attempts',
            started_at TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            last_accessed_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            INDEX idx_module_id (module_id),
            INDEX idx_content_id (content_id),
            INDEX idx_status (status),
            INDEX idx_user_module (user_id, module_id),
            INDEX idx_user_content (user_id, content_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES training_modules(id) ON DELETE CASCADE,
            FOREIGN KEY (content_id) REFERENCES training_contents(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_module_content (user_id, module_id, content_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
    ]
    
    try:
        async with engine.begin() as conn:
            for sql in create_tables_sql:
                await conn.execute(text(sql))
            print("✅ Training module tables created successfully!")
            
            # Insert sample training modules
            await insert_sample_data(conn)
            
    except Exception as e:
        print(f"❌ Error creating training tables: {e}")
        raise


async def insert_sample_data(conn):
    """Insert sample training data"""
    
    sample_data_sql = [
        # Sample training modules
        """
        INSERT IGNORE INTO training_modules (id, title, description, module_order, is_active, estimated_duration_minutes, created_by) VALUES
        (1, 'Area Coordinator Basics', 'Introduction to the role and responsibilities of an Area Coordinator', 1, TRUE, 30, 1),
        (2, 'Property Management', 'Learn how to manage and coordinate properties in your area', 2, TRUE, 45, 1),
        (3, 'Customer Service Excellence', 'Best practices for providing excellent customer service', 3, TRUE, 25, 1),
        (4, 'Safety and Compliance', 'Important safety guidelines and compliance requirements', 4, TRUE, 35, 1);
        """,
        
        # Sample training contents
        """
        INSERT IGNORE INTO training_contents (id, module_id, content_type, title, content, content_order, is_required, video_duration_seconds) VALUES
        (1, 1, 'TEXT', 'Welcome to Area Coordination', 'Welcome to your new role as an Area Coordinator! This module will introduce you to the key responsibilities and expectations of your position.', 1, TRUE, NULL),
        (2, 1, 'VIDEO', 'Area Coordinator Overview Video', 'https://example.com/videos/area-coordinator-overview.mp4', 2, TRUE, 300),
        (3, 1, 'QUIZ', 'Area Coordinator Basics Quiz', 'Test your understanding of the Area Coordinator role', 3, TRUE, NULL),
        
        (4, 2, 'TEXT', 'Property Management Introduction', 'Learn the fundamentals of property management and coordination in your assigned area.', 1, TRUE, NULL),
        (5, 'VIDEO', 'Property Inspection Process', 'https://example.com/videos/property-inspection.mp4', 2, TRUE, 450),
        (6, 2, 'DOCUMENT', 'Property Management Guidelines', 'https://example.com/documents/property-guidelines.pdf', 3, TRUE, NULL),
        (7, 2, 'QUIZ', 'Property Management Assessment', 'Test your knowledge of property management procedures', 4, TRUE, NULL),
        
        (8, 3, 'TEXT', 'Customer Service Principles', 'Understanding the core principles of excellent customer service in the hospitality industry.', 1, TRUE, NULL),
        (9, 3, 'VIDEO', 'Customer Interaction Best Practices', 'https://example.com/videos/customer-service.mp4', 2, TRUE, 600),
        (10, 3, 'QUIZ', 'Customer Service Quiz', 'Test your customer service knowledge', 3, TRUE, NULL),
        
        (11, 4, 'TEXT', 'Safety Guidelines', 'Important safety guidelines that all Area Coordinators must follow.', 1, TRUE, NULL),
        (12, 4, 'VIDEO', 'Emergency Procedures', 'https://example.com/videos/emergency-procedures.mp4', 2, TRUE, 400),
        (13, 4, 'DOCUMENT', 'Compliance Checklist', 'https://example.com/documents/compliance-checklist.pdf', 3, TRUE, NULL),
        (14, 4, 'QUIZ', 'Safety and Compliance Test', 'Final assessment on safety and compliance', 4, TRUE, NULL);
        """,
        
        # Update quiz questions
        """
        UPDATE training_contents SET quiz_questions = '{
            "q1": {"question": "What is the primary responsibility of an Area Coordinator?", "options": ["Manage properties", "Handle customer complaints", "Coordinate area operations", "All of the above"], "correct": "All of the above"},
            "q2": {"question": "How often should property inspections be conducted?", "options": ["Weekly", "Monthly", "Quarterly", "As needed"], "correct": "Monthly"},
            "q3": {"question": "What should you do in case of an emergency?", "options": ["Handle it yourself", "Call emergency services immediately", "Wait for instructions", "Ignore it"], "correct": "Call emergency services immediately"}
        }' WHERE id = 3;
        """,
        
        """
        UPDATE training_contents SET quiz_questions = '{
            "q1": {"question": "What is the first step in property management?", "options": ["Inspection", "Documentation", "Communication", "Planning"], "correct": "Planning"},
            "q2": {"question": "How should property issues be reported?", "options": ["Verbally", "In writing", "Via app", "All of the above"], "correct": "All of the above"},
            "q3": {"question": "What is the most important aspect of property coordination?", "options": ["Speed", "Accuracy", "Communication", "Cost"], "correct": "Communication"}
        }' WHERE id = 7;
        """,
        
        """
        UPDATE training_contents SET quiz_questions = '{
            "q1": {"question": "What is the golden rule of customer service?", "options": ["Be fast", "Be polite", "Treat others as you want to be treated", "Be available 24/7"], "correct": "Treat others as you want to be treated"},
            "q2": {"question": "How should you handle difficult customers?", "options": ["Ignore them", "Be patient and understanding", "Escalate immediately", "Argue back"], "correct": "Be patient and understanding"},
            "q3": {"question": "What is the most important communication skill?", "options": ["Speaking", "Listening", "Writing", "Reading"], "correct": "Listening"}
        }' WHERE id = 10;
        """,
        
        """
        UPDATE training_contents SET quiz_questions = '{
            "q1": {"question": "What should you do if you notice a safety hazard?", "options": ["Ignore it", "Report it immediately", "Fix it yourself", "Wait for someone else"], "correct": "Report it immediately"},
            "q2": {"question": "How often should safety equipment be checked?", "options": ["Daily", "Weekly", "Monthly", "Yearly"], "correct": "Monthly"},
            "q3": {"question": "What is the first step in an emergency?", "options": ["Call for help", "Assess the situation", "Evacuate immediately", "Take photos"], "correct": "Assess the situation"}
        }' WHERE id = 14;
        """,
        
        # Set passing scores
        """
        UPDATE training_contents SET passing_score = 70 WHERE content_type = 'QUIZ';
        """
    ]
    
    try:
        for sql in sample_data_sql:
            await conn.execute(text(sql))
        print("✅ Sample training data inserted successfully!")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not insert sample data: {e}")


if __name__ == "__main__":
    asyncio.run(create_training_tables())
