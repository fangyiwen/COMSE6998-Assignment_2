# COMSE6998 Assignment 2: Voice Controlled Photo Album

## Inroduction
Implement a photo album web application, that can be searched using natural language through both text and voice. Use Lex, ElasticSearch, and Rekognition to create an intelligent search layer to query your photos for people, objects, actions, landmarks and more.

Amazon S3 Endpoint: http://myawsbucket-comse6998-assignment2-cf.s3-website-us-east-1.amazonaws.com

## Architecture
![Architecture](doc/AWS_architecture.png)

## Instruction
1. Create two CloudFormations on the Console. One is for the whole app architecture including Lambda using empty/nullresource template. One is for CodePipeline using CodePipeline template. Only update lambda via Pipeline. Do not update from CF Console. "COMSE6998-HW2-VoiceControlledPhotoAlbum-T1" followed by "COMSE6998-HW2-VoiceControlledPhotoAlbum-CodePipeline".
2. Commit the two GitHub repos to get the auto deployment.
3. Do modify the hard-coded code such as frontend API SDK, ES URL, S3 bucket, identification info in Lambda/API, etc.

## Note
- HTTP voice access
    - Add the S3 link to chrome://flags/#unsafely-treat-insecure-origin-as-secure
    - https://piazza.com/class/kjqgku8rz0z6ei?cid=470
- Uploaded photo filename
    - Filename must be no space and only alphanumeric
