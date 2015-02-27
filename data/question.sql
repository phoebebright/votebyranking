
SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

BEGIN;
INSERT INTO `web_question` VALUES ('1', 'As a member of this committee I...', 'How do you feel at this time', 'P', '0', null), ('2', 'Our committee is', 'How do you think the committee is functioning at the moment', 'P', '0', null);
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
