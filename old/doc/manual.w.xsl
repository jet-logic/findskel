<xsl:stylesheet version="1.0" xsl:exclude-result-prefixes="xi xsl" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output encoding="ascii"  method="xml" />
	<xsl:template match="/">
		<page>
			<title>fileop.py</title>
			<category>Python</category>
			<content type='xhtml'>
				<xsl:copy-of select="html/body/node()" />
			</content>
		</page>
	</xsl:template>
</xsl:stylesheet>
