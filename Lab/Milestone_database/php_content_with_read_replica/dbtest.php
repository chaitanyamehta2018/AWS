<?php
// Primary DB (writes)
$primaryHost = "mydb.ct220c0o6jam.ap-south-1.rds.amazonaws.com";
$primaryUser = "dbadmin";
$primaryPass = "Indian@123";
$primaryDB   = "myDatabase";

// Replica DB (reads)
$replicaHost = "mydb-read-replica.ct220c0o6jam.ap-south-1.rds.amazonaws.com";
$replicaUser = "dbadmin";
$replicaPass = "Indian@123";
$replicaDB   = "myDatabase";

try {
    // Writer connection
    $pdoWrite = new PDO("mysql:host=$primaryHost;dbname=$primaryDB", $primaryUser, $primaryPass);
    $pdoWrite->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Reader connection
    $pdoRead = new PDO("mysql:host=$replicaHost;dbname=$replicaDB", $replicaUser, $replicaPass);
    $pdoRead->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("DB connection failed: " . $e->getMessage());
}
?>
