def update_submodules()
	puts 'Updating submodules'

	puts 'git config submodule.cloud_deployer.url'
	`git config submodule.cloud_deployer.url https://github.com/davidsulpy/cloud_deployer.git`
	puts 'git submodule init'
	`git submodule init`
	puts 'git submodule update'
	`git submodule update`
end

ACCESS_KEY_ID = ENV['isakid'] || ENV["initialstate.access_key_id"]
SECRET_ACCESS_KEY = ENV['issak'] || ENV["initialstate.secret_access_key"]
ENVIRONMENT = ENV["env"] || 'dev'

task :default => [:push_to_s3] do
	puts "Finished!"
end

task :get_cloud_deployer do
	update_submodules()
	require_relative 'cloud_deployer/cloud_deploy'
end

task :push_to_s3 => [:get_cloud_deployer] do
	@s3helper = CloudDeploy::S3Helper.new({
		:access_key_id => ACCESS_KEY_ID,
		:secret_access_key => SECRET_ACCESS_KEY
		})
	asset_bucket = "get-dev.initialstate.com"
	if (ENVIRONMENT == 'prod')
		asset_bucket = "get.initialstate.com"
	end
	@s3helper.put_asset_in_s3("install_scripts/*", asset_bucket, "", "text/plain")
end