USE landonvolkman_ogwdis;

CREATE TABLE ogAccount(
email VARCHAR(320) NOT NULL,
password VARCHAR(512) NOT NULL,
defaultAccount VARCHAR(15),
defaultWindow VARCHAR(20),
PRIMARY KEY (email)
);

CREATE TABLE word(
phrase VARCHAR(140) NOT NULL,
badness INT,
PRIMARY KEY (phrase)
);

CREATE TABLE twitterAccount(
handle VARCHAR(15) NOT NULL,
email VARCHAR(320) NOT NULL,
password VARCHAR(512),
durationStart TIMESTAMP NOT NULL, #split into two for ease of use,need to update er/schema
durationEnd TIMESTAMP NOT NULL,
associatedAccount VARCHAR(320) UNIQUE,
followers INT NOT NULL,
PRIMARY KEY (handle)
-- , FOREIGN KEY (associatedAccount) REFERENCES ogAccount (email)
);

ALTER TABLE ogAccount ADD FOREIGN KEY (defaultAccount) REFERENCES twitterAccount(handle);

CREATE TABLE tweet(
tweetID INT NOT NULL,
handle VARCHAR(15) NOT NULL,
date date NOT NULL,# API ex. Tue May 14 17:54:29 +0000 2019 
time TIMESTAMP NOT NULL,
content VARCHAR(200),
retweet INT,
favorites INT,
replies INT,
link VARCHAR(256),
PRIMARY KEY (tweetID),
FOREIGN KEY (handle) REFERENCES twitterAccount (handle)
);

CREATE TABLE composedOf(
phrase VARCHAR(140) NOT NULL,
tweetID INT,
PRIMARY KEY (phrase, tweetID),
FOREIGN KEY(tweetID) REFERENCES tweet (tweetID)
);

CREATE TABLE causes(
followEventID INT NOT NULL,
tweetID INT NOT NULL,
PRIMARY KEY(followEventID, tweetID),
FOREIGN KEY(tweetID) REFERENCES tweet (tweetID)
);

CREATE TABLE follower(
handle VARCHAR(15) NOT NULL,
PRIMARY KEY (handle)
);

CREATE TABLE followEvent(
followEventID INT NOT NULL,
associatedFollower VARCHAR(15),
date DATE NOT NULL,
time TIMESTAMP NOT NULL,
gainOrLoss INT NOT NULL,
associatedTweet INT,
associatedAccount VARCHAR(15),
PRIMARY KEY (followEventID),
FOREIGN KEY (associatedFollower) REFERENCES follower (handle),
FOREIGN KEY (associatedTweet) REFERENCES tweet (tweetID),
FOREIGN KEY (associatedAccount) REFERENCES twitterAccount (handle),
CHECK (gainOrLoss = -1 or gainOrLoss = 1)
);

CREATE TABLE followedBy(
followerHandle VARCHAR(15) NOT NULL,
accountHandle VARCHAR(15) NOT NULL,
PRIMARY KEY(followerHandle, accountHandle),
FOREIGN KEY(followerHandle) REFERENCES follower(handle),
FOREIGN KEY(accountHandle) REFERENCES twitterAccount(handle)
);

INSERT INTO ogAccount VALUES ('parksh@outlook.com', 'password.10', '@treeexclusive');
INSERT INTO ogAccount VALUES ('eidac@att.net', 'abcd.431', '@applejuice');
INSERT INTO ogAccount VALUES ('singh@yahoo.com', 'qwerty123!', '@twitch');
INSERT INTO ogAccount VALUES ('grossman@gmail.com', '1q2w3e4r!', '@horsegirl');
INSERT INTO ogAccount VALUES ('druschel@aol.com', 'myn00b#12', '@livelaughlove');
INSERT INTO ogAccount VALUES ('nachbaur@msm.com', 'qwertyuiop.2', '@rick335');
INSERT INTO ogAccount VALUES ('mschwartz@aol.com', 'maintain#3', '@siccskate');
INSERT INTO ogAccount VALUES ('valdez@yahoo.com', 'password1!', '@walmart99');
INSERT INTO ogAccount VALUES ('jesse@comcast.com', 'password2!', '@egg620');

INSERT INTO word VALUES ('hate', 5);
INSERT INTO word VALUES ('evil', 4);
INSERT INTO word VALUES ('retweet', 4);
INSERT INTO word VALUES ('math', 3);
INSERT INTO word VALUES ('trump', 3);
INSERT INTO word VALUES ('war', 2);
INSERT INTO word VALUES ('wall', 1);
INSERT INTO word VALUES ('cats', 1);
INSERT INTO word VALUES ('ride', 1);



INSERT INTO twitterAccount VALUES ('@treeexclusive', 'jtcm@gmail.com', 'qwerty.21', '2019-08-29 02:26:79', '2019-08-29 04:55:23', 'parksh@outlook.com', 125); 
INSERT INTO twitterAccount VALUES ('@applejuice', 'ai8jn@yahoo.com', 'abcde.53', '2019-08-29 10:05:39', '2019-08-29 12:30:01', 'eidac@att.net', 534); 
INSERT INTO twitterAccount VALUES ('@twitch', 'singh@yahoo.com', 'qwerty123!', '2019-08-30 03:35:19', '2019-08-30 03:58:22', 'singh@yahoo.com', 745); 
INSERT INTO twitterAccount VALUES ('@horsegirl', 'gromanss@gmail.com', 'qwertyuiop.2', '2019-08-30 02:12:55', '2019-08-30 2:14:41', 'grossman@gmail.com', 364); 
INSERT INTO twitterAccount VALUES ('@livelaughlove', 'dreul@yahoo.com', 'abcd.1234', '2019-08-31 08:39:52', '2019-09-01 9:03:32', 'druschel@aol.com', 356); 
INSERT INTO twitterAccount VALUES ('@rick335', 'nefks@aol.com', 'user123!!', '2019-08-31 07:49:31', '2019-08-31 08:44:26', 'nachbaur@msm.com', 1176); 
INSERT INTO twitterAccount VALUES ('@footbal942', 'jwarren@icloud', '3rjs1laqe', '2019-08-31 01:32:12', '2019-08-31 02:17:09', 'eidac@att.net', 47); 
INSERT INTO twitterAccount VALUES ('@siccskate', 'msw74@gmail.com', 'secure#12', '2019-08-31 03:08:32', '2019-08-31 03:10:45', 'mschwartz@aol.com', 532); 
INSERT INTO twitterAccount VALUES ('@walmart99', 'valdez@yahoo.com', 'password1!', '2019-09-01 08:56:21', '2019-09-01 09:12:21', 'valdez@yahoo.com', 12); 
INSERT INTO twitterAccount VALUES ('@egg620', 'jesse3@icloud.com', 'eggegg00!', '2019-09-01 11:17:23', '2019-09-01 12:32:49', 'jesse@comcast.com', 5890); 


INSERT INTO tweet VALUES (143, '@walmart99', '2019-09-01', '2019-09-01 09:03:29', 'I hate the Jonas Brothers', 1, 17, 3, 'https://twitter.com/i/web/status/1128357932238823424');
INSERT INTO tweet VALUES (321, '@egg620', '2019-09-01', '2019-09-01 11:40:12', 'evil: every villain is lemons', 105, 137, 32, 'https://twitter.com/i/web/status/184890203945840293');
INSERT INTO tweet VALUES (378, '@siccskate', '2019-08-31', '2019-08-31 03:09:43', 'retweet if you are my friend', 15, 3, 2, 'https://twitter.com/i/web/status/128394730239502935920');
INSERT INTO tweet VALUES (436, '@livelaughlove', '2019-08-31', '2019-08-31 09:01:07', 'math should be banished', 8, 10, 2, 'https://twitter.com/i/web/status/90850398590834345');
INSERT INTO tweet VALUES (489, '@egg620', '2019-09-01', '2019-09-01 11:29:11', 'trump is the best president ever', 67, 88, 17, 'https://twitter.com/i/web/status/598738202958902');
INSERT INTO tweet VALUES (527, '@applejuice', '2019-08-29', '2019-08-29 11:15:21', 'i think we need more war', 5, 11, 9, 'https://twitter.com/i/web/status/19294950332838950284');
INSERT INTO tweet VALUES (621, '@livelaughlove', '2019-08-31', '2019-08-31 08:54:22', 'build that wall', 5, 9, 4, 'https://twitter.com/i/web/status/1982347582616289485921');
INSERT INTO tweet VALUES (693, '@horsegirl', '2019-08-30', '2019-08-30 02:13:15', 'i love my cats', 22, 47, 11, 'https://twitter.com/i/web/status/2930580982714658693490');
INSERT INTO tweet VALUES (732, '@twitch', '2019-08-30', '2019-08-30 03:39:22', 'can anyone give me a ride?', 1, 1, 2, 'https://twitter.com/i/web/status/23450629492034950');
INSERT INTO tweet VALUES (319, '@egg620', '2019-09-01', '2019-09-01 11:48:52', 'i like eggs', 105, 21, 11, 'https://twitter.com/i/web/status/192983928129203021');
INSERT INTO tweet VALUES (344, '@egg620', '2019-09-01', '2019-09-01 11:44:43', 'tom brady sucks', 122, 88, 24, 'https://twitter.com/i/web/status/199029292029298392');
INSERT INTO tweet VALUES (519, '@egg620', '2019-09-01', '2019-09-01 12:28:39', 'real eyes realize real lies', 412, 202, 18, 'https://twitter.com/i/web/status/19289238029832991');
INSERT INTO tweet VALUES (667, '@egg620', '2019-09-01', '2019-09-01 12:30:27', 'anyone want to play donkey konga 2?', 22, 99, 23, 'https://twitter.com/i/web/status/1902738219837473626');

INSERT INTO followEvent VALUES (25, '@john392','2019-08-30', '2019-08-30 02:13:28', '1', 693, '@horsegirl');
INSERT INTO followEvent VALUES (67, '@lilbreezy','2019-09-01', '2019-09-01 12:19:47', '-1', 489, '@egg620');
INSERT INTO followEvent VALUES (102, '@yeehaw98','2019-08-31', '2019-08-31 03:10:29', '-1', 378, '@siccskate');
INSERT INTO followEvent VALUES (116, '@sarahbills','2019-08-31', '2019-08-31 08:58:53', '1', 621, '@livelaughlove');
INSERT INTO followEvent VALUES (152, '@jenna2112','2019-08-29', '2019-08-29 12:18:53', '1', 527, '@appliejuice');
INSERT INTO followEvent VALUES (179, '@breeanan','2019-08-31', '2019-08-31 09:02:36', '-1', 436, '@livelaughlove');
INSERT INTO followEvent VALUES (201, '@jjorange','2019-09-01', '2019-09-01 11:56:17', '1', 321, '@egg620');
INSERT INTO followEvent VALUES (217, '@hahioh','2019-09-01', '2019-09-01 09:08:50', '-1', 143, '@walmart99');
INSERT INTO followEvent VALUES (63, '@drphil','2019-09-01', '2019-09-01 12:23:47', '1', 519, '@egg620');
INSERT INTO followEvent VALUES (77, '@oprah','2019-09-01', '2019-09-01 11:55:22', '1', 519, '@egg620');
INSERT INTO followEvent VALUES (89, '@ellen','2019-09-01', '2019-09-01 12:03:31', '-1', 519, '@egg620');
INSERT INTO followEvent VALUES (90, '@josh','2019-09-01', '2019-09-01 12:14:43', '-1', 667, '@egg620');
INSERT INTO followEvent VALUES (109, '@kyle','2019-09-01', '2019-09-01 11:36:11', '-1', 667, '@egg620');

drop table followEvent;

INSERT INTO follower VALUES ('@drphil');
INSERT INTO follower VALUES ('@oprah');
INSERT INTO follower VALUES ('@ellen');
INSERT INTO follower VALUES ('@josh');
INSERT INTO follower VALUES ('@kyle');
INSERT INTO follower VALUES ('@lilbreezy');
INSERT INTO follower VALUES ('@yeehaw98');
INSERT INTO follower VALUES ('@sarahbills');
INSERT INTO follower VALUES ('@jenna2112');
INSERT INTO follower VALUES ('@breeanan');
INSERT INTO follower VALUES ('@jjorange');
INSERT INTO follower VALUES ('@hahioh');

INSERT INTO causes VALUES (25, 693);
INSERT INTO causes VALUES (67, 489);
INSERT INTO causes VALUES (102, 378);
INSERT INTO causes VALUES (116, 621);
INSERT INTO causes VALUES (152, 527);
INSERT INTO causes VALUES (179, 436);
INSERT INTO causes VALUES (201, 321);
INSERT INTO causes VALUES (217, 143);

INSERT INTO followedBy VALUES ('@john392','@horsegirl');
INSERT INTO followedBy VALUES ('@lilbreezy','@egg620');
INSERT INTO followedBy VALUES ('@yeehaw98','@siccskate');
INSERT INTO followedBy VALUES ('@sarahbills','@livelaughlove');
INSERT INTO followedBy VALUES ('@jenna2112','@applejuice');
INSERT INTO followedBy VALUES ('@breeanan','@livelaughlove');
INSERT INTO followedBy VALUES ('@jjorange','@egg620');
INSERT INTO followedBy VALUES ('@hahioh','@walmart99');
INSERT INTO followedBy VALUES ('@drphil','@egg620');
INSERT INTO followedBy VALUES ('@oprah','@egg620');
INSERT INTO followedBy VALUES ('@ellen','@egg620');
INSERT INTO followedBy VALUES ('@josh','@egg620');
INSERT INTO followedBy VALUES ('@kyle','@egg620');

INSERT INTO composedOf VALUES ('hate', 143);
INSERT INTO composedOf VALUES ('evil', 321);
INSERT INTO composedOf VALUES ('retweet', 378);
INSERT INTO composedOf VALUES ('math', 436);
INSERT INTO composedOf VALUES ('trump', 489);
INSERT INTO composedOf VALUES ('war', 527);
INSERT INTO composedOf VALUES ('wall', 621);
INSERT INTO composedOf VALUES ('cats', 693);
INSERT INTO composedOf VALUES ('ride', 732);
