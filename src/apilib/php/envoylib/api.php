<?php
/*
 * Envoy is more free software. It is licensed under the WTFPL, which
 * allows you to do pretty much anything with it, without having to
 * ask permission. Commercial use is allowed, and no attribution is
 * required. We do politely request that you share your modifications
 * to benefit other developers, but you are under no enforced
 * obligation to do so :)
 * 
 * Please read the accompanying LICENSE document for the full WTFPL
 * licensing text.
 */

namespace EnvoyLib;

class Api
{
	public function __construct($endpoint, $api_id, $api_key)
	{
		if(ends_with($endpoint, "/"))
		{
			$endpoint = substr($endpoint, 0, strlen($endpoint) - 1);
		}
		
		$this->endpoint = $endpoint;
		$this->id = $api_id;
		$this->key = $api_key;
	}
	
	public function DoRequest($method, $path, $arguments)
	{
		if(!starts_with($path, "/"))
		{
			$path = "/" . $path;
		}
		
		if(strtolower($method) == "get" && !empty($arguments))
		{
			$fields = array();
			
			foreach($arguments as $key => $value)
			{
				$fields[] = rawurlencode($key) . "=" . rawurlencode($value);
			}
			
			$path = $path . "?" . implode("&", $fields);
		}
		
		$url = $this->endpoint . $path;
		$curl = curl_init();
		
		curl_setopt_array($curl, array(
			CURLOPT_URL		=> $url,
			CURLOPT_RETURNTRANSFER	=> true,
			CURLOPT_USERAGENT	=> "Envoy PHP API Library/{$envoy_apilib_version}",
			CURLOPT_HTTPHEADER	=> array(
				"Envoy-API-Id: {$this->id}",
				"Envoy-API-Key: {$this->key}"
			)
		));
		
		if(strtolower($method) == "post")
		{
			curl_setopt_array($curl, array(
				CURLOPT_POST		=> true,
				CURLOPT_POSTFIELDS	=> $arguments
			));
		}
		
		if($result = curl_exec($curl))
		{
			$json = json_decode($result, true);
			$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);
			
			switch($status)
			{
				case 200:
					/* All went perfectly. */
					return $json["response"];
				case 400:
					/* Bad or incomplete request data was provided. */
					throw new BadDataException("The provided arguments were invalid or incomplete.");
				case 401:
					/* The client is not authenticated. */
					throw new NotAuthenticatedException("No valid API credentials were provided.");
				case 403:
					/* The client is trying to access or modify a resource they are not permitted to access. */
					throw new NotAuthorizedException("The provided API credentials do not grant access to this resource or operation.");
				case 404:
					switch($json["type"])
					{
						case "path":
							/* The specified API path does not exist (or the wrong method was used). */
							throw new ApiException("An invalid API path was specified.");
						case "resource":
							/* The specified resource does not exist. */
							throw new NotFoundException("The specified resource does not exist.");
					}
				case 409:
					/* The client tried to create a resource that already exists. */
					throw new AlreadyExistsException("A resource with the specified identifier already exists.");
				default:
					throw new ApiException("An unrecognized status code ({$status}) was returned.");
			}
		}
		else
		{
			$error = curl_error($curl);
			$errno = curl_errno($curl);
			throw new UnknownException("cURL failed with error {$errno} ({$error})");
		}
	}
	
	public function User($username, $fqdn)
	{
		return new User($username, $fqdn, $this);
	}
	
	public function CreateUser($username, $fqdn, $password)
	{
		$this->DoRequest("post", "/user/register", array(
			"username"	=> $username,
			"fqdn"		=> $fqdn,
			"password"	=> $password
		));
		
		return $this->User($username, $fqdn);
	}
}