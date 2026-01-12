# save this as shell.nix
{ pkgs ? import <nixpkgs> {}}:

pkgs.mkShell {
  packages = with pkgs;[ 
    python312
    python312Packages.pip
    python312Packages.virtualenv
 ];
}
