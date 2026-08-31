{
  description = "ccamel GitHub profile development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };

  outputs =
    { nixpkgs, ... }:
    let
      supportedSystems = [
        "aarch64-darwin"
        "x86_64-linux"
        "aarch64-linux"
      ];

      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.actionlint
              pkgs.bash-language-server
              pkgs.deadnix
              pkgs.git
              pkgs.markdownlint-cli2
              pkgs.marksman
              pkgs.nil
              pkgs.nixfmt
              pkgs.prettier
              pkgs.statix
              pkgs.yaml-language-server
              pkgs.yamllint
            ];
          };
        }
      );
    };
}
