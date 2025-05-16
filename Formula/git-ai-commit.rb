class GitAiCommit < Formula
  include Language::Python::Virtualenv
  
  desc "AI-powered git commit message generator using Claude"
  homepage "https://github.com/lieblius/git-ai-commit"
  url "https://github.com/lieblius/git-ai-commit/archive/refs/tags/v0.0.1.tar.gz"
  sha256 "UPDATE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "poetry" => :build
  depends_on "python@3.11"
  depends_on "nvim"

  def install
    virtualenv_create(libexec, "python3.11")
    system "poetry", "build", "--format=wheel"
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      You need to set your Anthropic API key:
        export ANTHROPIC_API_KEY=your_api_key_here
    EOS
  end

  test do
    # Basic help test
    system "#{bin}/gcai", "--help"
  end
end