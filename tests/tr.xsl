<?xml version="1.0" encoding="utf-8"?>

<!--
  Kopete History to Text Stylesheet 0.1

  (C) Copyright 2007 Bram Schoenmakers <bramschoenmakers@kde.nl>
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  exclude-result-prefixes='xsl str'
                version="1.0">

<xsl:output method="text" />

<xsl:param name="day" select="''"/>
<xsl:param name="shortnicks" select="'no'"/>
<xsl:param name="shownicks" select="'no'" />
<xsl:param name="showtime" select="'no'"/>

<xsl:template match="kopete-history">
  <xsl:if test="@version!=0.9">
    <xsl:text>NOTE: The stylesheet written for version 0.9 of the Kopete History. Your history doesn't seem to match this version. This may have resulted in wrong output.</xsl:text>
  </xsl:if>
  <xsl:call-template name="listcontacts"/><xsl:text>
</xsl:text>
  <!-- Filter for day number if one was specified. -->
  <xsl:for-each select="msg[$day='' or contains($day,normalize-space(substring(@time,1,2)))]">
    <!-- Check if this is the first node, or if the date from the previous msg is different from the current one. In that case, print a date. -->
    <xsl:if test="position()=1 or (normalize-space(substring(@time,1,2)) != normalize-space(substring(preceding-sibling::msg[position()=1]/@time,1,2)))">
      <xsl:text>
</xsl:text>
      <xsl:call-template name="date"/>
      <xsl:text>

</xsl:text>
    </xsl:if>
    <xsl:apply-templates select="."/>
  </xsl:for-each>

  <xsl:text>


Generated with the kopete2text XSLT sheet by Bram Schoenmakers &lt;me@bramschoenmakers.nl&gt;</xsl:text>
</xsl:template>

<xsl:template name="listcontacts">
  <xsl:text>Kopete History from </xsl:text>
  <xsl:for-each select="/kopete-history/head/contact[not(@type)]">
    <xsl:value-of select="@contactId"/>
    <xsl:choose>
      <xsl:when test="position()=last()-1">
        <xsl:text> and </xsl:text>
      </xsl:when>
      <xsl:when test="position() >= 1 and position() != last()">
        <xsl:text>, </xsl:text>
      </xsl:when>
    </xsl:choose>
  </xsl:for-each>
</xsl:template>

<xsl:template name="date">
  <xsl:value-of select="normalize-space(substring(@time,1,2))" />
  <xsl:text> </xsl:text>
  <xsl:variable name="month" select="../head/date/@month" />
  <xsl:choose>
    <xsl:when test="$month=1">
      <xsl:text>January</xsl:text>
    </xsl:when>
    <xsl:when test="$month=2">
      <xsl:text>February</xsl:text>
    </xsl:when>
    <xsl:when test="$month=3">
      <xsl:text>March</xsl:text>
    </xsl:when>
    <xsl:when test="$month=4">
      <xsl:text>April</xsl:text>
    </xsl:when>
    <xsl:when test="$month=5">
      <xsl:text>May</xsl:text>
    </xsl:when>
    <xsl:when test="$month=6">
      <xsl:text>June</xsl:text>
    </xsl:when>
    <xsl:when test="$month=7">
      <xsl:text>July</xsl:text>
    </xsl:when>
    <xsl:when test="$month=8">
      <xsl:text>August</xsl:text>
    </xsl:when>
    <xsl:when test="$month=9">
      <xsl:text>September</xsl:text>
    </xsl:when>
    <xsl:when test="$month=10">
      <xsl:text>October</xsl:text>
    </xsl:when>
    <xsl:when test="$month=11">
      <xsl:text>November</xsl:text>
    </xsl:when>
    <xsl:when test="$month=12">
      <xsl:text>December</xsl:text>
    </xsl:when>
  </xsl:choose>
  <xsl:text> </xsl:text>
  <xsl:value-of select="../head/date/@year" />
</xsl:template>

<xsl:template name="time">
  <!-- We need to fix the displayed time, because the XML strips away all leading zeros before minutes and seconds. -->

  <!-- Parse time field -->
  <xsl:variable name="hours" select="substring-before( substring-after(@time, ' '), ':')" />
  <xsl:variable name="minutes" select="substring-before( substring-after( @time, ':' ), ':' )" />
  <xsl:variable name="seconds" select="substring-after( substring-after( @time, ':' ), ':' )" />

  <xsl:if test="string-length($hours)=1">
    <xsl:text>0</xsl:text>
  </xsl:if>
  <xsl:value-of select="$hours" />
  <xsl:text>:</xsl:text>

  <xsl:if test="string-length($minutes)=1">
    <xsl:text>0</xsl:text>
  </xsl:if>
  <xsl:value-of select="$minutes" />
  <xsl:text>:</xsl:text>

  <xsl:if test="string-length($seconds)=1">
    <xsl:text>0</xsl:text>
  </xsl:if>
  <xsl:value-of select="$seconds" />
</xsl:template>

<xsl:template match="msg">
  <xsl:if test="$showtime='yes' or $showtime='y' or $showtime='1'">
    <xsl:text>[</xsl:text>
    <xsl:call-template name="time"/>
    <xsl:text>] </xsl:text>
  </xsl:if>
  <xsl:if test="$shownicks='no' or $shownicks='n' or $shownicks='0'">
    <xsl:if test="@in='1'">
      <xsl:text>&lt;&lt;&lt; </xsl:text>
    </xsl:if>
    <xsl:if test="@in='0'">
      <xsl:text>&gt;&gt;&gt; </xsl:text>
    </xsl:if>
  </xsl:if>
  <xsl:if test="$shownicks='yes' or $shownicks='y' or $shownicks='1'">
    <xsl:if test="$shortnicks='yes' or $shortnicks='y' or $shortnicks='1'">
      <xsl:value-of select="substring-before(concat(@nick,' '),' ')"/>
    </xsl:if>
    <xsl:if test="$shortnicks='no' or $shortnicks='n' or $shortnicks='0'">
      <xsl:value-of select="@nick" />
    </xsl:if>
    <xsl:text>: </xsl:text>
  </xsl:if>
  <xsl:value-of select="." /><xsl:text>
</xsl:text>
</xsl:template>

</xsl:stylesheet>
