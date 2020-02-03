#!/usr/bin/perl --

use DBI;
use CGI;
use Encode;

my $CGI = new CGI;
my $DBH;
my $sth,$res;
my $sql;
my $db_source;
my $blogid = $CGI->param("l_blogid");
my $spotid = $CGI->param("l_spotid");
my $simplemode=$CGI->param("simplemode");
if($spotid){
   $simplemode=1;
}else{
   $spotid = $CGI->param("spotid");
}

my $daylimit = $CGI->param("daylimit");
my $totallimit = $CGI->param("totallimit");
my $cart_group = $CGI->param("cart_group");
my $btp_group = $CGI->param("btp_group");
my $spotseq   = $CGI->param("spotseq");
my $mode = $CGI->param("mode");
#20101207に追加
my $updatemode = $CGI->param("updatemode");


	my $IMPDBSERVER="192.168.10.220";
	my $ZMASTERSERVER="192.168.10.220";

	#mad2.0対応
	#ログ保存ファイル
	my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	my $logfile="./logs/sql_".(1900+$year).($mon+1).$mday.".log";
	open (FILE, ">>$logfile") or die "$!";
print  FILE "\n".(1900+$year).($mon+1).$mday." ".$hour.":".$min.":".$sec."\n";
print  FILE "\nspotid=".$spotid;
	#mad2.0用
	$match=$CGI->param("match");
	$retargeting=$CGI->param("retargeting");
	$impression=$CGI->param("impression");
	$behavior=$CGI->param("behavior");
	$premium=$CGI->param("premium");
	$category=$CGI->param("category");
	$mark_retargeting=$CGI->param("mark_retargeting");
	$potential_match=$CGI->param("potential_match");
	$broadreach=$CGI->param("broadreach");
        $adctrl_retargeting=$CGI->param("adctrl_retargeting");
        $btpremium=$CGI->param("btpremium2");
        $ca_retargeting=$CGI->param("caretarget2");
#20101207 audience対応追加
        $audience=$CGI->param("audience");

my @item=('ca_retargeting','btpremium','match','retargeting','impression','behavior','premium','category','mark_retargeting','potential_match','broadreach','adctrl_retargeting','audience');

unless($blogid || $spotid || $mode eq 'publish'){
  print "Content-type: text/html; charset=utf-8\n\n";
  print "<html><head><title>CA-SETTING</title></head><body>";
  print "<a href='/cartj/setWhiteListBlogSide'>setWhiteListBlogSide</a><br>";
  print "<a href='/cartj/setWhiteListClientSide'>setWhiteListClientSide</a><br>";
  print "<a href='/cart/setBlogLimit'>setBlogLimit</a>";
  print "</body></html>";
  exit;
}
#20101216追加
my $myspotinfo="";
print FILE "\nblogid=".$blogid;

if(!$blogid){
 if($spotid){
      $myspotinfo=spotinfo($spotid);
      $spotseq=0;
      $blogid=0;
      if($myspotinfo){
        $spotseq=$myspotinfo->[0];
        $blogid=$myspotinfo->[1];
      }else{
         $spotidmessage=1065;
      }
 }
}
print FILE "blogid=".$blogid.";spotseq=".$spotseq.";spotid=".$spotid."\n";

$db_source = 'DBI:mysql:affiliate_db:'.$ZMASTERSERVER;
$DBH = DBI->connect($db_source, 'blog', 'RqU4e6bXvvGjM') || die $DBH->errstr;
$sql = "SELECT blogid,blogname FROM affiliate_db.blog_info WHERE blogid = ?";
print FILE $sql."\n";
$sth = $DBH->prepare($sql);
$sth->execute($blogid);
if($res = $sth->fetchrow_arrayref()){
  $blogname = $res->[1];
}else{
  $message = 1000;
}
if($blogid == 0){$message = 1000;}
$sth->finish();

my %blog_spot_info;
$sql  = "SELECT bsi.spotseq as spotseq,bsi.spotid as spotid,bsi.spotname as spotname,bsi.spottype as spottype,bti.typeid,concat(bti.width,'x',bti.height) as spotsize";
$sql .= " FROM ad_info_db.blog_spot_info as bsi , ad_info_db.banner_type_info as bti";
$sql .= " WHERE bsi.sizetypeid = bti.typeid and bsi.blogid = ?";
#if($spotid){
#$sql .= " AND bsi.spotid = '".$spotid."'";
#}
print FILE $sql;
$sth = $DBH->prepare($sql);
$sth->execute($blogid);
while($res = $sth->fetchrow_arrayref()){
  $dat = "";
  $spotseq_tmp = "";
  $cnt = 0;
  for $colname (@{$sth->{NAME_lc}}){
    if($colname eq "spotseq"){
      $spotseq_tmp = $res->[$cnt];
    }else{
      $dat .= sprintf ('"%s" : "%s",', $colname,$res->[$cnt]);
    }
    $cnt++;
  }
  if($dat){
    $blog_spot_info{$spotseq_tmp} = $dat; 
  }
}

$sth->finish();


if($mode eq "insert" ){
 print FILE "insert MODE\n";
 print FILE "blogid=".$blogid.",blog_group=".$cart_group;

 if(checkSpotseqExisted($blogid,$spotseq)==1){
  $sql = qq{
             INSERT INTO affiliate_db.buying_pvlimit_info (blogid,blog_group)
             VALUES (?,?)
  };
 print FILE $sql;
  $sth = $DBH->prepare($sql);
  $sth->execute($blogid,$cart_group);
  $sth->finish();
  print "blogid=".$blogid.",blog_group=".$btp_group;
  $sql = qq{
             INSERT INTO affiliate_db.buying_pvlimit_info (blogid,blog_group)
             VALUES (?,?)
  };
  print FILE $sql;
  $sth = $DBH->prepare($sql);
  $sth->execute($blogid,$btp_group);
  $sth->finish();
    print FILE "blogid=".$blogid.";blog_group=0";
  $sql = qq{
             INSERT IGNORE INTO affiliate_db.buying_pvlimit_info (blogid,blog_group)
             VALUES (?,0)
  };
  print FILE $sql;
  $sth = $DBH->prepare($sql);
  $sth->execute($blogid);
  $sth->finish();
 }else{
  #spotseq正当ではありません
  $message=1064;
 }

}

$DBH->disconnect();


$db_source = 'DBI:mysql:cart_info:'.$IMPDBSERVER.';';

$DBH = DBI->connect($db_source, 'blog', 'RqU4e6bXvvGjM') or die $DBI::errstr;

if($mode eq "publish"){
  $sql = qq{
            SELECT *
            FROM blogid_limit_info 
  };
  $sth = $DBH->prepare($sql);
  $sth->execute();
  print "Content-Disposition: attachment; filename=blogid_limit_info.csv\n";
  print "Content-type: application/octet-stream\n\n";

  for $colname (@{$sth->{NAME_lc}}){
    push(@colname,$colname);
    push(@printfstr,"%s");
  }
  print '"'.join('","',@colname).'"'."\n";
  $printfstr = '"'.join('","',@printfstr).'"'."\n";

  while ($res = $sth->fetchrow_arrayref()) {
    $data = sprintf($printfstr,@{$res});
    Encode::from_to($data,"UTF-8","Shift_JIS");
    print $data;
  }
  $sth->finish();
  $DBH->disconnect();
  exit;
}

#mad1.0設定を無くして、defaultのdivision値をBOTHに設定する
    $division = "BOTH";

if($mode eq "update" ){
  print  FILE "mode=update\n";
  print  FILE "para=$division,$daylimit,$totallimit,$daylimit,$totallimit,$blogid,$cart_group,$btp_group";
 print  FILE "updatemode=".$updatemode."\n";
 if($updatemode == 1){
  $sql = qq{UPDATE blogid_limit_info SET division = ?,daylimit = ?,totallimit = ? WHERE blogid = ? AND cart_group = ? AND btp_group = ?};
  print FILE $sql;
  $sth = $DBH->prepare($sql) or die $DBH->errstr;
  $sth->execute($division,$daylimit,$totallimit,$blogid,$cart_group,$btp_group) or die $sth->errstr;
  $sth->finish();
#  $DBH->commit or die $DBH->errstr;
 }
 if($updatemode == 2){
  $message=CamptypeFilterInfo($division,$blogid,$spotseq,"update");
  print  FILE $message."\n";
 }

}

if($mode eq "insert" ){
# blogid,spotseqごとに重複チェック
if(checkBlogExisted($blogid,$spotseq)==0 && checkSpotseqExisted($blogid,$spotseq)==1){
print FILE "blogid_limit_infoデータ更新開始"."\n";
  
  $sql = qq{
           INSERT INTO blogid_limit_info(blogid,cart_group,btp_group,division,daylimit,totallimit,daylyimp,totalimp,spotseq) VALUES (?,?,?,?,?,?,?,?,?)
  };
   print FILE $sql."\n";
  $sth = $DBH->prepare($sql);
  $sth->execute($blogid,$cart_group,$btp_group,$division,$daylimit,$totallimit,0,0,$spotseq);
  $message = $sth->err;
  $sth->finish();

  if(!$message){
   $message=CamptypeFilterInfo($division,$blogid,$spotseq,"insert",$other);
  }

 }else{
  #spotseq重複
  $message=1063;
 }
}


print FILE "message=".$message."\n";

if($blogid){
$sql = qq{
           SELECT blogid,cart_group,btp_group,division,daylimit,totallimit,daylyimp,totalimp,spotseq FROM blogid_limit_info 
           WHERE blogid = ? 
};
}
if($simplemode == 1){
if($spotid){
 $sql = qq{
           SELECT blogid,cart_group,btp_group,division,daylimit,totallimit,daylyimp,totalimp,spotseq FROM blogid_limit_info WHERE blogid = ? and spotseq = $spotseq 
 };  

}

}

$sql .= " ORDER BY spotseq";
 

print FILE $sql."blogid=".$blogid."\n";


$sth = $DBH->prepare($sql);
$sth->execute($blogid);

print "content-type: text/plain;charset=utf-8\n\n";
#print '{ "data" : [ ';

while($res = $sth->fetchrow_arrayref()){
  $cnt=0;
  $spotseq_tmp = "";
  $dat = "{ ";
  for $colname (@{$sth->{NAME_lc}}){
    $dat .= sprintf ('"%s" : "%s",', $colname,$res->[$cnt]);
    if($colname eq 'spotseq'){
        $spotseq_tmp = $res->[$cnt];
      #新規mad2.0部分追加
       if($mycamptype=getCampType($blogid,$spotseq_tmp)){
        print FILE "blogid=".$blogid.",spotseq=".$spotseq_tmp."data=".$mycamptype;
         $dat .= sprintf ('"%s" : "%s",', 'camptype',$mycamptype);
       }else{
         print FILE "blogid=".$blogid.",spotseq=".$spotseq_tmp."data=no camptypefilterinfor";
         $dat .= sprintf ('"%s" : "%s",', 'camptype',''); 
       }
    }
    $cnt++;
  }
  $dat .= $blog_spot_info{$spotseq_tmp}; 
 
  chop($dat);
  $dat2 .= $dat. "},";
}
chop($dat2);

#print FILE $dat2;

#unused spotseq list
if($blogid){
  $spotseqs=&spotseqNotUsed($blogid);
}
my $spotidleft;
my $data1;
print FILE @$spotseqs;
foreach $myseq (@$spotseqs) {
    print FILE "unused spotseq=".$myseq;
    $data1 = "{ ";
    $data1.='"spotseq" : "'.$myseq.'",'.$blog_spot_info{$myseq};
    chop($data1);
    $spotidleft.=$data1. "},";
}
chop($spotidleft);
print FILE $spotidleft;
print FILE $dat2;
if($spotidmessage){$message=$spotidmessage;}
print '{"data1" : ['.$spotidleft.'], "data" : ['.$dat2.'], "simplemode" : "'.$simplemode.'", "blogid" : "'.$blogid.'", "blogname" : "'.$blogname.'", "message" : "'.$message.'" }';
$sth->finish();

$DBH->disconnect();
print FILE "last para:".$division."-".$blogid."-".$spotseq;
close(FILE);
exit;

sub spotinfo{
   my ($spotid)=@_;
   my $myserver=$ZMASTERSERVER;
   my $mydb="ad_info_db";
   my $seqSQL=qq{
             SELECT spotseq,blogid
              FROM  blog_spot_info
              WHERE  spotid = ?
             };
    print FILE $seqSQL."\n";
   my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
   my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

   my $sth = $myDBH->prepare($seqSQL);
   $sth->execute($spotid);
   my $retval="";
    while ($res = $sth->fetchrow_arrayref()){
      $retval=$res;
    }
    $sth->finish();
    print FILE "spotseq=".$retval->[0]."blogid=".$retval->[1]."\n";
   return $retval;

}

sub spotseqNotUsed{
   my ($blogid)=@_;
   my @dat=();
   my $myserver=$ZMASTERSERVER;
   my $mydb="ad_info_db";
   $usedspotseqs=spotseqUsed($blogid);
    print FILE $blogid.$usedspotseqs;
$spotseq_left = qq{SELECT spotseq FROM blog_spot_info WHERE blogid = ? and spotseq not in ($usedspotseqs) };
   print FILE $spotseq_left;
   my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
   my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

   my $sth = $myDBH->prepare($spotseq_left);
   $sth->execute($blogid);
  
    while ($res = $sth->fetchrow_arrayref()){
      push (@dat,$res->[0]);
    }
 return \@dat;

}
sub getCampType{
  my ($blogid,$spotseq)=@_;
    print FILE "blogid=".$blogid.",spotseq=".$spotseq."\n";

  my $myserver=$ZMASTERSERVER;
   my $mydb="ad_info_db";
   my $SQL=qq{
             SELECT a.camptype 
              FROM  camptype_filter_info a , blog_spot_info b
              WHERE b.blogid=? AND b.spotseq=? AND a.spotid=b.spotid
             };
    print FILE $SQL."\n";
   my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
   my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

   my $sth = $myDBH->prepare($SQL);
   $sth->execute($blogid,$spotseq);
   my $retval="";
    while ($res = $sth->fetchrow_arrayref()){
      $retval.=$res->[0].",";
    }
    $sth->finish();
    print FILE "camptypeinfo=".$retval."\n";
   return $retval;

}

sub checkBlogExisted{
   my ($blogid,$spotseq)=@_;
   print FILE "存在確認"."\n";
   print FILE "blogid=".$blogid."-spotseq=".$spotseq;
   my $myserver=$IMPDBSERVER;
   my $mydb="cart_info";
   my $SQL=qq{
             SELECT blogid
              FROM  blogid_limit_info
              WHERE blogid=? AND spotseq=? limit 1
             };
    print FILE $SQL."\n";
   my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
   my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

   my $sth = $myDBH->prepare($SQL);
    $sth->execute($blogid,$spotseq);
   my $flag=0;
    if($res = $sth->fetchrow_arrayref()){
      $flag=1;
    }
    $sth->finish();

 print FILE "flag=".$flag."\n";
  return $flag;
}

sub checkSpotseqExisted{
   my ($blogid,$spotseq) = @_;
   print FILE " checkSpotseqExisted 開始\n";
   print FILE "blogid=".$blogid.",spotseq=".$spotseq;
   my $myserver=$ZMASTERSERVER;
   my $mydb="ad_info_db";
   my $spotid="";
   my $SQL=qq{
             SELECT spotid
              FROM  blog_spot_info
              WHERE blogid=? AND spotseq=?
             };

  my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
  my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

  my $sth = $myDBH->prepare($SQL);
  $sth->execute($blogid,$spotseq);
  my $flag=0;
  if($res = $sth->fetchrow_arrayref()){
   $flag = 1;
  }
  $sth->finish();
  print FILE "spotid=".$spotid."\n";
  return $flag;
}

sub spotseqUsed{
 my ($blogid) = @_;
 my $sql = qq{ SELECT spotseq FROM blogid_limit_info WHERE blogid = ? };
 print FILE $sql;
 my $myserver=$IMPDBSERVER;
 my $mydb="cart_info";
 my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
 my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

  my $sth = $myDBH->prepare($sql);
  $sth->execute($blogid);
  while($res = $sth->fetchrow_arrayref()){
   $spotids .= $res->[0].",";
  }
  $spotids .="0";
 return $spotids;
}




sub CamptypeFilterInfo{
   my ($division,$blogid,$spotseq,$exeType,$other) = @_;
   print FILE "CamptypeFilterInfo更新\n";
   print FILE "para=$division,$blogid,$spotseq,$exeType";
   my $myserver=$ZMASTERSERVER;
   my $mydb="ad_info_db";
   my $mytable="camptype_filter_info";
   my $spotid="";
   my $SQL=qq{ 
             SELECT spotid 
              FROM  blog_spot_info
              WHERE blogid=? AND spotseq=?
             };

  my $mydb_source = 'DBI:mysql:'.$mydb.':'.$myserver.';';
  my $myDBH = DBI->connect($mydb_source, 'blog', 'RqU4e6bXvvGjM');

  my $sth = $myDBH->prepare($SQL);
  $sth->execute($blogid,$spotseq);
  while($res = $sth->fetchrow_arrayref()){
   $spotid = $res->[0];
  }
  print FILE "spotid=".$spotid."\n";
 my $message="";
 my $filtertype='white';
#更新操作
if($exeType eq "update"){

   #既存データ状態を取得

 if($spotid){
   #既存削除(同時に使うもあるので)
  my $SQL=qq{
              DELETE 
              FROM  camptype_filter_info
              WHERE spotid=? AND filtertype=? 
             };
   print FILE $SQL."\n";
   $sth = $myDBH->prepare($SQL);
   $sth->execute($spotid,$filtertype);
   $exeType="insert";
 }else{
   $message=1064;
 }
}

#挿入操作
 if ($exeType eq "insert"){

if($spotid){

 #mad2.0他のデータ挿入
 print FILE "mad2.0新規DB処理\n";
 foreach my $key (@item){
  $value=$$key;
  #設定された値で更新する
  if($value){
     print FILE $key."=".$value."\n";
     $camptype=$key;
      $exeSQL=qq{
       INSERT IGNORE INTO camptype_filter_info(spotid,filtertype,camptype) VALUES (?,?,?)
      };
     print FILE $exeSQL."\n";
     $sth = $myDBH->prepare($exeSQL);
     $sth->execute($spotid,$filtertype,$camptype);
     if(!$message){
          $message = $sth->err; 
     }
  }

 }  

}else{
  #spotid存在なし
  $message=1064;
}

}

$sth->finish();
 return $message;
}
