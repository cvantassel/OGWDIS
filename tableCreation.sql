use landonvolkmann_ogwdis;

create table OG_Account (Email varchar(50) PRIMARY KEY NOT NULL,
 Password varchar(256),
 DefaultAccount varchar(50)
 );
 
create table Tweet (TweetID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 Handle varchar(50) NOT NULL,
 DateAndTime DATETIME NOT NULL, 
 Content varchar(280) NOT NULL,
 Retweets INT not null,
 Favorites Int not null,
 link varchar(200));
 
create table TwitterAccount (Handle varchar(50) PRIMARY KEY NOT NULL,
 Email varchar(50) not null,
 Password varchar(256),
 DurationWindow int not null,
 AssociatedAccount varchar(50) not null);
 
create table FollowEvent (FollowEventID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
AssociatedFollower varchar(50) NOT NULL,
GainOrLoss int NOT NULL,
AssociatedTweet int not null,
AssociatedAccount varchar(50) NOT NULL);

create table causes (AssociatedFollowEventID int not null,
AssociatedTweet int not null);

create table Follower