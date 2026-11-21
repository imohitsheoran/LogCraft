USE logicraft;
DELIMITER $$
CREATE PROCEDURE seed_demo_records()
BEGIN
  DECLARE finished BOOLEAN DEFAULT FALSE;
  DECLARE mod_name VARCHAR(50);
  DECLARE idx INT DEFAULT 1;
  DECLARE mod_cursor CURSOR FOR SELECT module_name FROM (
    SELECT 'vehicles' module_name UNION ALL SELECT 'fuel' UNION ALL SELECT 'routes' UNION ALL SELECT 'drivers'
    UNION ALL SELECT 'inventory' UNION ALL SELECT 'receiving' UNION ALL SELECT 'picking' UNION ALL SELECT 'warehouse'
    UNION ALL SELECT 'shipments' UNION ALL SELECT 'deliveries' UNION ALL SELECT 'notifications' UNION ALL SELECT 'proof-of-delivery'
    UNION ALL SELECT 'schedules' UNION ALL SELECT 'fares' UNION ALL SELECT 'bookings' UNION ALL SELECT 'transit'
  ) modules;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished = TRUE;
  OPEN mod_cursor;
  module_loop: LOOP
    FETCH mod_cursor INTO mod_name;
    IF finished THEN LEAVE module_loop; END IF;
    SET idx = 1;
    WHILE idx <= 10 DO
      INSERT INTO records(module, name, status, reference, location, quantity)
      SELECT mod_name, CONCAT(REPLACE(UPPER(mod_name),'-',' '),' record ', LPAD(idx,2,'0')),
        ELT((idx % 4)+1,'In Transit','Available','Needs Review','Active'),
        CONCAT(UPPER(LEFT(mod_name,3)),'-',1000+idx),
        ELT((idx % 3)+1,'North Hub','Central Depot','South Yard'), 100-(idx*3)
      WHERE NOT EXISTS (SELECT 1 FROM records WHERE module=mod_name AND reference=CONCAT(UPPER(LEFT(mod_name,3)),'-',1000+idx));
      SET idx = idx + 1;
    END WHILE;
  END LOOP;
  CLOSE mod_cursor;
END$$
DELIMITER ;
CALL seed_demo_records();
DROP PROCEDURE seed_demo_records;

-- User password hashes are generated at application startup from the configured demo password.
