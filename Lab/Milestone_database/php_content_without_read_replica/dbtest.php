<?php
// Primary DB (writer + reader)
$servername = "mydb.ct220c0o6jam.ap-south-1.rds.amazonaws.com";
$username   = "dbadmin";
$password   = "Indian@123";
$database   = "myDatabase";

try {
    $pdo = new PDO("mysql:host=$servername;dbname=$database", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Primary DB connection failed: " . $e->getMessage());
}
?>
