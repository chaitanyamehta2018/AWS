Precondition: This lab is to be created using the root account instead of Admin account.
========================================================================================

1. Create the S3 bucket
	Go to S3 in the AWS console.
	Click Create bucket.
	Enter a globally unique name (e.g., my-access-point-lab-bucket).
	Choose Region = ap-south-1 (Mumbai).
	Keep default settings, click Create bucket.
	After creating bucket, create folders app1 and app2 inside the bucket.

2. Delegating the access control to access points.
		{
		  "Version": "2012-10-17",
		  "Statement": [
			{
			  "Effect": "Allow",
			  "Principal": {
				"AWS": "*"
			  },
			  "Action": "*",
			  "Resource": [
				"arn:aws:s3:::my-access-point-lab-bucket",
				"arn:aws:s3:::my-access-point-lab-bucket/*"
			  ],
			  "Condition": {
				"StringEquals": {
				  "s3:DataAccessPointAccount": "994626601075"
				}
			  }
			}
		  ]
		}
	
3. Create IAM Users
	You’ll need two users for this lab: User-1 and User-2.
	Go to IAM → Users → Create user.
	Name: User-1	
	Select "Access key - Programmatic access".
	Save the Access Key ID and Secret Access Key securely.
	Repeat for User-2.
	
	using CLI:
		aws iam create-user --user-name user1
		aws iam create-login-profile --user-name user1 --password "Hello@123" --no-password-reset-required
		
		aws iam create-user --user-name user2
		aws iam create-login-profile --user-name user2 --password "Hello@123" --no-password-reset-required





3. Create S3 Access Points
	We’ll create two Access Points pointing to the same bucket.
	Go to S3 → Access Points → Create access point.
	Name: access-point-1
	Bucket: my-access-point-lab-bucket
	Network origin = Internet
	Give the  policy as following json.
	Click Create.
	Repeat for access-point-2.


	{
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Principal": {
					"AWS": "arn:aws:iam::994626601075:user/user1"
				},
				"Action": "s3:PutObject",
				"Resource": "arn:aws:s3:ap-south-1:994626601075:accesspoint/access-point-1/object/app1/*"
			}
		]
	}
	

	{
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Principal": {
					"AWS": "arn:aws:iam::994626601075:user/user2"
				},
				"Action": "s3:PutObject",
				"Resource": "arn:aws:s3:ap-south-1:994626601075:accesspoint/access-point-2/object/app2/*"
			}
		]
	}



4.  Give IAM permission to users to allow of s3 access point.
	From IAM-->Policy-->Create the policy named : access-point-user-access-policy
		{
			"Version": "2012-10-17",
			"Statement": [
				{
					"Effect": "Allow",
					"Action": [
						"s3:ListAccessPoints",
						"s3:GetAccessPoint",
						"s3:ListBucket"
					],
					"Resource": "*"
				}
			]
		}
		
5. For both the user1 and user2 attached the created policy: access-point-user-access-policy.

6. Test & validation steps:
	Verify that User1 can upload only to app1 via Access Point 1
	Verify that User2 can upload only to app2 via Access Point 2
	Cross-access attempts fail.
