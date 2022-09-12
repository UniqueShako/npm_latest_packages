rule preinstall {
	meta: 
		description = "Checks the package.json manifest to see if the package runs any preinstall scripts"
	strings:
		$x1 = "preinstall" ascii nocase
	condition:
		all of them
}
