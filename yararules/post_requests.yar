rule post_request{
   meta:
        data="2022-09-06"
        author="Team 3"
        description="Common POST request information gathering attack."
   strings:
        $a="os.homedir()" nocase ascii
        $b="os.hostname()" nocase ascii
        $c="dns.getServers()" nocase ascii
        $d="POST" ascii
      
   
   condition:
        all of them
}