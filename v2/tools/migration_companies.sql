-- Create user and business
INSERT OR IGNORE INTO businesses (name, address) VALUES
('hotel1', 'Naamlaan 154');

INSERT OR IGNORE INTO businesses (name, address) VALUES
('hotel2', 'Naamlaan 155');

INSERT OR IGNORE INTO businesses (name, address) VALUES
('hotel3', 'Naamlaan 156');

-- user met meerdere voertuigen koppelen aan een business
UPDATE users
SET business_id = 1
WHERE id = (
  SELECT user_id
  FROM vehicles
  GROUP BY user_id
  HAVING COUNT(*) > 1
  LIMIT 1
);