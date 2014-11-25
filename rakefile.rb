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
VERSION = `git describe --tags --long`

task :default => [:push_to_s3, :invalidate_cloudfront] do
	puts "Finished!"
end

task :deploy => [:release_version, :push_to_s3, :invalidate_cloudfront] do
	puts "Finished!"
end

task :get_cloud_deployer do
	update_submodules()
	require_relative 'cloud_deployer/cloud_deploy'
end

task :release_version do
	begin
		`fullrelease --no-input`
	rescue
		puts "error: perhaps zest.releaser isn't installed, install and try again"
	end
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
	@s3helper.put_asset_in_s3("install_scripts/python", asset_bucket, "", "text/plain")
end

task :invalidate_cloudfront do
	puts "beginning cache invalidation"
	cf_distro_id = 'E1M7UGJXW11IYK'
	if (ENVIRONMENT == 'prod')
		cf_distro_id = 'EXNTGBZ947DQ1'
	end
	@cloudFrontHelper = CloudDeploy::CloudFrontHelper.new({
		:access_key_id => ACCESS_KEY_ID,
		:secret_access_key => SECRET_ACCESS_KEY,
		:cf_distro_id => cf_distro_id,
		:code_version => VERSION
		})

	@cloudFrontHelper.invalidate("/python")

	puts "request submitted!"
end