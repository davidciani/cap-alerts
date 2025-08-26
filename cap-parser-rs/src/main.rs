use quick_xml::de::from_str;
use serde::Deserialize;
use std::{error::Error, fs};

#[derive(Debug, Deserialize)]
enum Status {
    Actual,
    Excercise,
    System,
    Test,
    Draft,
}

#[derive(Debug, Deserialize)]
enum MsgType {
    Alert,
    Update,
    Cancel,
    Ack,
    Error,
}

#[derive(Debug, Deserialize)]
enum Scope {
    Public,
    Restricted,
    Private,
}

#[derive(Debug, Deserialize)]
enum Category {
    Geo,
    Met,
    Safety,
    Security,
    Rescue,
    Fire,
    Health,
    Env,
    Transport,
    Infra,
    CBRNE,
    Other,
}

#[derive(Debug, Deserialize)]
enum ResponseType {
    Shelter,
    Evacuate,
    Prepare,
    Execute,
    Avoid,
    Monitor,
    Assess,
    AllClear,
    None,
}

#[derive(Debug, Deserialize)]
enum Urgency {
    Immediate,
    Expected,
    Future,
    Past,
    Unknown,
}

#[derive(Debug, Deserialize)]
enum Severity {
    Extreme,
    Severe,
    Moderate,
    Minor,
    Unknown,
}

#[derive(Debug, Deserialize)]
enum Certainty {
    Observed,
    Likely,
    Possible,
    Unlikely,
    Unknown,
}
#[derive(Debug, Deserialize)]
struct Value {
    #[serde(rename = "valueName")]
    value_name: String,
    value: String,
}

#[derive(Debug, Deserialize)]
struct Resource {
    #[serde(rename = "resourceDesc")]
    resource_desc: String,
    #[serde(rename = "mimeType")]
    mime_type: String,
    size: Option<String>,
    uri: Option<String>,
    #[serde(rename = "derefUri")]
    deref_uri: Option<String>,
    digest: Option<String>,
}

#[derive(Debug, Deserialize)]
struct Area {
    #[serde(rename = "areaDesc")]
    area_desc: String,
    polygon: Option<Vec<String>>,
    circle: Option<Vec<String>>,
    geocode: Option<Vec<Value>>,
    altitude: Option<String>,
    ceiling: Option<String>,
}

#[derive(Debug, Deserialize)]
struct AlertInfo {
    language: String,
    category: Vec<Category>,
    event: String,
    #[serde(rename = "responseType")]
    response_type: Option<ResponseType>,
    urgency: Urgency,
    severity: Severity,
    certainty: Certainty,
    audiance: Option<String>,
    event_codes: Option<Vec<Value>>,
    effective: Option<String>,
    onset: Option<String>,
    expires: Option<String>,
    sender_name: Option<String>,
    headline: Option<String>,
    description: Option<String>,
    instruction: Option<String>,
    web: Option<String>,
    contact: Option<String>,
    parameter: Option<Vec<Value>>,
    resource: Option<Vec<Resource>>,
    area: Option<Vec<Area>>,
}

#[derive(Debug, Deserialize)]
struct Alert {
    identifier: String,
    sender: String,
    sent: String,
    status: Status,
    #[serde(rename = "msgType")]
    msg_type: MsgType,
    source: Option<String>,
    scope: Scope,
    restriction: Option<String>,
    addresses: Option<String>,
    code: Option<Vec<String>>,
    note: Option<String>,
    references: Option<String>,
    incidents: Option<String>,
    info: Option<Vec<AlertInfo>>,
}

#[derive(Debug, Deserialize)]
struct AlertList {
    #[serde(rename = "alert")]
    alerts: Vec<Alert>,
}

fn main() -> Result<(), Box<dyn Error>> {
    println!("Hello, world!");

    let xml_string = r#"
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>OnSolve-b434161a298440ea805e64bb8eed2d9b</identifier>
        <sender>ssewell@thomson-mcduffie.net</sender>
        <sent>2025-01-30T14:58:26-05:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <source>GA McDuffie County Board of Commissioners</source>
        <scope>Public</scope>
        <code>IPAWSv1.0</code>
        <info>
            <language>en-US</language>
            <category>Safety</category>
            <event>Local Area Emergency</event>
            <responseType>Avoid</responseType>
            <urgency>Expected</urgency>
            <severity>Extreme</severity>
            <certainty>Observed</certainty>
            <eventCode>
                <valueName>SAME</valueName>
                <value>LAE</value>
            </eventCode>
            <effective>2025-01-30T14:58:26-05:00</effective>
            <expires>2025-01-30T16:58:26-05:00</expires>
            <senderName>201971,GA McDuffie County Board of Commissioners,</senderName>
            <headline>Local Area Emergency</headline>
            <parameter>
                <valueName>EAS-ORG</valueName>
                <value>CIV</value>
            </parameter>
            <parameter>
                <valueName>BLOCKCHANNEL</valueName>
                <value>EAS</value>
            </parameter>
            <parameter>
                <valueName>BLOCKCHANNEL</valueName>
                <value>NWEM</value>
            </parameter>
            <parameter>
                <valueName>WEAHandling</valueName>
                <value>Public Safety</value>
            </parameter>
            <parameter>
                <valueName>CMAMtext</valueName>
                <value>Old Milledgeville Rd., Maddox Creek Rd., are closed until further notice. Use
                    Caution.</value>
            </parameter>
            <parameter>
                <valueName>CMAMlongtext</valueName>
                <value>Our county roads are experiencing the burden of Hurricane Helene and
                    continued heavy rains Old Milledgeville Rd., Maddox Creek Rd., George McDuffie
                    Rd., and Haynes Rd. are closed until further notice. Please avoid affected areas
                    and exercise caution when traveling. Local officials are working to address the
                    damage as quickly as possible.</value>
            </parameter>
            <parameter>
                <valueName>timezone</valueName>
                <value>EST</value>
            </parameter>
            <area>
                <areaDesc>GA McDuffie County Board of Commissioners</areaDesc>
                <geocode>
                    <valueName>SAME</valueName>
                    <value>013189</value>
                </geocode>
            </area>
        </info>
        <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
            <SignedInfo>
                <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" />
                <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" />
                <Reference URI="">
                    <Transforms>
                        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />
                    </Transforms>
                    <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" />
                    <DigestValue>267kSkG4bznqkcf/YdIPNmyusIAVurKaIfmQdQ7DjXQ=</DigestValue>
                </Reference>
            </SignedInfo>
            <SignatureValue>
                PivFL7vK/We5u1wTrL1ggcA1Z67xnpNLpGA//tehR+kZ6+YDR6ZFsXVDlLj6uCX5vIn5LtuDmwx9Rz7pB8hFGrOSss0YrrAyh9MSuCU0lxN4UQxHNWKWHtn88dBHjakDs4fix8FCjtPcCUNSnyoJVZladwnZk1ox3EYHmbSoxin3iY/5f1o8xGSzh8KUbmRN4gBRN2JIoWUDzKS+SaeL5RZMggN+bUxPbAezGhg+r2iIzTruK68qdlJIuwMee6xU6q8kXuX6A3ZGVI8Q8hrME7BvmFl2farDdONRM0BuZc69IPxN840Z4ut58F5JEgUK23Zfw+UJ0Z302uPMosK4Vw==</SignatureValue>
            <KeyInfo>
                <X509Data>
                    <X509Certificate>
                        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</X509Certificate>
                </X509Data>
            </KeyInfo>
        </Signature>
    </alert>
    "#;
    //let xml_content = fs::read_to_string("/Users/david/data_projects/cap-alerts/data/20250705_162303/IpawsArchivedAlerts_2025-01_001.xml")?;

    // Deserialize the XML string into the Alert struct
    let alert: Alert = from_str(&xml_string)?;

    println!("{:?}", alert);
    Ok(())
}
